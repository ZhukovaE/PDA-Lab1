import json
from pathlib import Path
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from db import engine, asteroids, close_approaches, init_db

DATA_DIR = Path("data")
CHUNK = 100


def iter_records():
    """Генератор: (asteroid_dict, approach_dict) по всем JSON-файлам."""
    for f in sorted(DATA_DIR.glob("feed_*.json")):
        payload = json.loads(f.read_text(encoding="utf-8"))
        neo_by_date = payload.get("near_earth_objects", {})
        for _date_str, items in neo_by_date.items():
            for neo in items:
                diam = neo.get("estimated_diameter", {}).get("kilometers", {})
                ast = {
                    "id": neo["id"],
                    "name": neo["name"],
                    "absolute_magnitude_h": neo.get("absolute_magnitude_h"),
                    "diameter_km_min": diam.get("estimated_diameter_min"),
                    "diameter_km_max": diam.get("estimated_diameter_max"),
                    "is_potentially_hazardous": int(bool(neo.get("is_potentially_hazardous_asteroid"))),
                    "is_sentry_object": int(bool(neo.get("is_sentry_object"))),
                    "nasa_jpl_url": neo.get("nasa_jpl_url"),
                }
                for ca in neo.get("close_approach_data", []):
                    if not ca.get("close_approach_date"):
                        continue
                    yield ast, {
                        "neo_id": neo["id"],
                        "close_approach_date": ca["close_approach_date"],
                        "epoch_date_close_approach": int(ca["epoch_date_close_approach"]),
                        "velocity_kmh": float(ca["relative_velocity"]["kilometers_per_hour"]),
                        "miss_distance_km": float(ca["miss_distance"]["kilometers"]),
                        "orbiting_body": ca.get("orbiting_body"),
                    }


def load_all():
    init_db()

    asteroids_map = {}
    approaches = []
    for ast, ca in iter_records():
        asteroids_map[ast["id"]] = ast
        approaches.append(ca)

    print(f"Астероидов (уникальных): {len(asteroids_map)}")
    print(f"Сближений (всего):       {len(approaches)}")

    with engine.begin() as conn:
        if asteroids_map:
            stmt = sqlite_insert(asteroids).values(list(asteroids_map.values()))
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
            conn.execute(stmt)

        inserted = 0
        for i in range(0, len(approaches), CHUNK):
            chunk = approaches[i:i + CHUNK]
            stmt = sqlite_insert(close_approaches).values(chunk)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["neo_id", "epoch_date_close_approach"]
            )
            res = conn.execute(stmt)
            inserted += res.rowcount or 0

    print(f"Вставлено новых сближений: {inserted}")


if __name__ == "__main__":
    load_all()
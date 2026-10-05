import pandas as pd
from sqlalchemy import text
from db import engine

pd.set_option("display.width", 180)
pd.set_option("display.max_columns", 20)


def run(sql: str, params: dict | None = None) -> pd.DataFrame:
    """sqlalchemy-текст + pandas.read_sql."""
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


SQL_1 = """
SELECT
    strftime('%Y', close_approach_date) AS year,
    COUNT(*)                            AS approaches_cnt,
    COUNT(DISTINCT neo_id)              AS unique_asteroids
FROM close_approaches
GROUP BY year
ORDER BY year;
"""

SQL_2 = """
SELECT
    a.name,
    a.is_potentially_hazardous AS hazardous,
    c.close_approach_date,
    ROUND(c.velocity_kmh, 1)   AS velocity_kmh,
    ROUND(c.miss_distance_km)  AS miss_distance_km
FROM close_approaches c
JOIN asteroids a ON a.id = c.neo_id
ORDER BY c.velocity_kmh DESC
LIMIT 10;
"""

SQL_3 = """
SELECT
    a.is_potentially_hazardous        AS hazardous,
    COUNT(DISTINCT a.id)              AS asteroids_cnt,
    ROUND(AVG(a.diameter_km_max), 3)  AS avg_diameter_km,
    ROUND(AVG(c.miss_distance_km))    AS avg_miss_km,
    ROUND(MIN(c.miss_distance_km))    AS min_miss_km,
    ROUND(MAX(c.velocity_kmh))        AS max_velocity_kmh
FROM asteroids a
JOIN close_approaches c ON c.neo_id = a.id
GROUP BY a.is_potentially_hazardous
HAVING COUNT(DISTINCT a.id) > 5;
"""

SQL_4 = """
SELECT
    CASE
        WHEN miss_distance_km < 1e6 THEN '< 1 млн км'
        WHEN miss_distance_km < 5e6 THEN '1–5 млн км'
        WHEN miss_distance_km < 2e7 THEN '5–20 млн км'
        WHEN miss_distance_km < 1e8 THEN '20–100 млн км'
        ELSE '> 100 млн км'
    END                          AS distance_bucket,
    COUNT(*)                     AS cnt,
    ROUND(AVG(velocity_kmh))     AS avg_velocity_kmh
FROM close_approaches
GROUP BY distance_bucket
ORDER BY MIN(miss_distance_km);
"""

SQL_5 = """
SELECT
    a.name,
    a.is_potentially_hazardous        AS hazardous,
    ROUND(a.diameter_km_max, 3)       AS diameter_km,
    COUNT(*)                          AS approaches_cnt,
    ROUND(AVG(c.miss_distance_km))    AS avg_miss_km
FROM asteroids a
JOIN close_approaches c ON c.neo_id = a.id
GROUP BY a.id
HAVING COUNT(*) > 1
ORDER BY a.diameter_km_max DESC
LIMIT 5;
"""

SQL_6 = """
WITH ranked AS (
    SELECT
        strftime('%Y', c.close_approach_date) AS year,
        a.name,
        c.velocity_kmh,
        RANK() OVER (
            PARTITION BY strftime('%Y', c.close_approach_date)
            ORDER BY c.velocity_kmh DESC
        ) AS rnk
    FROM close_approaches c
    JOIN asteroids a ON a.id = c.neo_id
)
SELECT year, rnk, name, ROUND(velocity_kmh, 1) AS velocity_kmh
FROM ranked
WHERE rnk <= 3
ORDER BY year, rnk;
"""


def main():
    queries = {
        "1. Сближения по годам":          SQL_1,
        "2. Топ-10 самых быстрых":         SQL_2,
        "3. Опасные vs неопасные":         SQL_3,
        "4. Корзины по дистанции":         SQL_4,
        "5. Топ-5 крупных, летавших >1":   SQL_5,
        "6. Топ-3 быстрых в каждом году":  SQL_6,
    }
    for title, sql in queries.items():
        print("=" * 90)
        print(title)
        print("-" * 90)
        print(run(sql).to_string(index=False))
        print()


if __name__ == "__main__":
    main()
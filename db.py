import sqlite3
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Text, Integer, Float,
    ForeignKey, UniqueConstraint, Index,
)

DB_PATH = "nasa_neo.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
metadata = MetaData()

asteroids = Table(
    "asteroids", metadata,
    Column("id", Text, primary_key=True),
    Column("name", Text, nullable=False),
    Column("absolute_magnitude_h", Float),
    Column("diameter_km_min", Float),
    Column("diameter_km_max", Float),
    Column("is_potentially_hazardous", Integer, nullable=False, default=0),
    Column("is_sentry_object", Integer, nullable=False, default=0),
    Column("nasa_jpl_url", Text),
)

close_approaches = Table(
    "close_approaches", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("neo_id", Text, ForeignKey("asteroids.id"), nullable=False),
    Column("close_approach_date", Text, nullable=False),
    Column("epoch_date_close_approach", Integer, nullable=False),
    Column("velocity_kmh", Float),
    Column("miss_distance_km", Float),
    Column("orbiting_body", Text),
    UniqueConstraint("neo_id", "epoch_date_close_approach", name="uq_neo_epoch"),
)

Index("ix_ca_date", close_approaches.c.close_approach_date)
Index("ix_ca_neo", close_approaches.c.neo_id)


def init_db():
    """Создаёт таблицы, если их нет. Идемпотентно."""
    metadata.create_all(engine)


def get_connection():
    """Сырое sqlite3-соединение; для pandas.read_sql."""
    return sqlite3.connect(DB_PATH)
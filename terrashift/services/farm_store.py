"""Minimal SQLite farm observation ledger."""
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "farms.sqlite3"

def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("CREATE TABLE IF NOT EXISTS observations (id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, location TEXT, crop TEXT, planting_date TEXT, soil_type TEXT, observation TEXT, expenses REAL, harvest REAL, sales REAL)")

def add_observation(values):
    initialize()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT INTO observations(location,crop,planting_date,soil_type,observation,expenses,harvest,sales) VALUES(?,?,?,?,?,?,?,?)", values)

def list_observations():
    initialize()
    with sqlite3.connect(DB_PATH) as db:
        return db.execute("SELECT created_at,location,crop,planting_date,soil_type,observation,expenses,harvest,sales FROM observations ORDER BY id DESC").fetchall()

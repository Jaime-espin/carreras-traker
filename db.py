"""
Módulo simple para gestión de la base de datos SQLite de carreras.
Crea las tablas automáticamente y permite guardar o leer las carreras.
"""

import json
import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

DB_PATH = os.path.join("db", "carreras.db")
SCHEMA_PATH = os.path.join("db", "schema.sql")


def get_connection(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DB_PATH):
    """Crea las tablas de carreras y distancias si no existen."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                cursor.executescript(f.read())
        else:
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS carreras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    fecha DATE,
                    ciudad TEXT,
                    provincia TEXT,
                    tipo TEXT,
                    fuente TEXT,
                    link TEXT
                );
                CREATE TABLE IF NOT EXISTS distancias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    carrera_id INTEGER NOT NULL,
                    distancia_km REAL,
                    precio TEXT,
                    FOREIGN KEY (carrera_id) REFERENCES carreras(id)
                );
            """)
        conn.commit()
    logger.info("Base de datos inicializada correctamente.")


def guardar_carreras(carreras, db_path=DB_PATH):
    """Guarda una lista de carreras limpias en la base de datos."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM distancias;")
        cursor.execute("DELETE FROM carreras;")

        for c in carreras:
            cursor.execute("""
                INSERT INTO carreras (nombre, fecha, ciudad, provincia, tipo, fuente, link)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                c.get("nombre"),
                c.get("fecha"),
                c.get("ciudad"),
                c.get("provincia"),
                c.get("tipo"),
                c.get("fuente", "desconocido"),
                c.get("link")
            ))
            carrera_id = cursor.lastrowid

            for d in c.get("distancias", []):
                dist_km = d.get("distancia_km") if isinstance(d, dict) else d
                precio = d.get("precio") if isinstance(d, dict) else None
                cursor.execute("""
                    INSERT INTO distancias (carrera_id, distancia_km, precio)
                    VALUES (?, ?, ?)
                """, (carrera_id, dist_km, precio))

        conn.commit()
    logger.info(f"Guardadas {len(carreras)} carreras en {db_path}.")


def obtener_carreras(db_path=DB_PATH):
    """Lee todas las carreras con sus distancias desde SQLite."""
    if not os.path.exists(db_path):
        return []
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carreras ORDER BY fecha ASC;")
        rows = cursor.fetchall()
        carreras = []
        for r in rows:
            c = dict(r)
            cursor.execute("SELECT distancia_km, precio FROM distancias WHERE carrera_id = ?", (c["id"],))
            dists = [dict(d) for d in cursor.fetchall()]
            c["distancias"] = dists
            c["distancias_km"] = [d["distancia_km"] for d in dists if d["distancia_km"] is not None]
            carreras.append(c)
        return carreras


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    json_path = os.path.join("data", "carreras.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            datos = json.load(f)
        guardar_carreras(datos)
    else:
        init_db()

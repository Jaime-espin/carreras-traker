DROP TABLE IF EXISTS distancias;
DROP TABLE IF EXISTS carreras;

CREATE TABLE carreras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    fecha DATE,
    ciudad TEXT,
    provincia TEXT,
    tipo TEXT,
    fuente TEXT,
    link TEXT
);

CREATE TABLE distancias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carrera_id INTEGER NOT NULL,
    distancia_km REAL,
    precio TEXT,
    FOREIGN KEY (carrera_id) REFERENCES carreras(id)
);

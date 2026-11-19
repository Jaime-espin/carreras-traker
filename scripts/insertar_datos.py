import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

if __name__ == "__main__":
    json_path = os.path.join("data", "carreras.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            carreras = json.load(f)
        db.guardar_carreras(carreras)
        print(f"Insertadas {len(carreras)} carreras en la base de datos.")
    else:
        print(f"No se encontró {json_path}")

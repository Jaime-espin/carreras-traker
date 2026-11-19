from flask import Flask, render_template, jsonify
import json
import os
import db

app = Flask(__name__)

DATA_FILE = os.path.join("data", "carreras.json")


def load_carreras():
    """Carga las carreras de data/carreras.json o como respaldo desde SQLite."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return db.obtener_carreras()


@app.route("/")
def index():
    carreras = load_carreras()
    return render_template("index.html", carreras=carreras)


@app.route("/api/carreras")
def api_carreras():
    """Endpoint API opcional para obtener las carreras en formato JSON."""
    return jsonify(load_carreras())


if __name__ == "__main__":
    app.run(debug=True, port=5000)

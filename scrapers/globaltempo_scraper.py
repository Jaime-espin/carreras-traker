import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://www.global-tempo.com"


def get_race_details(race_url, session=None):
    if session is None:
        session = requests.Session()
    try:
        response = session.get(race_url)
    except requests.exceptions.SSLError:
        print(f"⚠️ SSL error en {race_url}, reintentando sin verify...")
        response = session.get(race_url, verify=False)
    except Exception as e:
        print(f"❌ Error de conexión con {race_url}: {e}")
        return {}

    if response.status_code != 200:
        print(f"Error al cargar {race_url}: {response.status_code}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    def safe_find_text(tag, prefix):
        el = soup.find(tag, text=lambda t: t and t.startswith(prefix))
        if el:
            return el.text.replace(prefix, "").strip()
        return "No encontrado"

    provincia = safe_find_text("h2", "Provincia :")
    localidad = safe_find_text("h2", "Localidad :")
    distancias_raw = safe_find_text("h2", "Distancia :")
    precios_raw = safe_find_text("h2", "PRECIO:")

    distancias = re.split(r"[/,\n]+", distancias_raw) if distancias_raw else []
    distancias = [d.strip() for d in distancias if d.strip()]

    precios = re.split(r"[/,\n]+", precios_raw) if precios_raw else []
    precios = [p.strip() for p in precios if p.strip()]

    return {
        "lugar": provincia + ', ' + localidad,
        "distancias": distancias,
        "precio": precios
    }


def get_globaltempo_races():
    session = requests.Session()
    try:
        response = session.get(BASE_URL)
    except requests.exceptions.SSLError:
        print("⚠️ SSL error en página principal, reintentando sin verify...")
        response = session.get(BASE_URL, verify=False)
    except Exception as e:
        print(f"❌ Error al conectar con {BASE_URL}: {e}")
        return []

    if response.status_code != 200:
        print(f"Error al cargar la página: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    enlaces = soup.find_all("a")
    carreras_basicas = []

    for a in enlaces:
        div = a.find("div", class_="cuadro_inscripcion")
        if div:
            nombre = div.find("h1").text.strip() if div.find("h1") else "Sin título"
            fecha = div.find("h2").text.strip() if div.find("h2") else "Sin fecha"
            resumen = div.get_text(separator="\n").strip()
            resumen = resumen.replace(nombre, "").replace(fecha, "").strip()

            link = a.get("href")
            link_completo = urljoin(BASE_URL, link)

            carreras_basicas.append({
                "nombre": nombre,
                "fecha": fecha,
                "link": link_completo,
                "resumen": resumen,
                "fuente": "globaltempo"
            })

    def fetch_details(carrera):
        detalles = get_race_details(carrera["link"], session)
        carrera.update(detalles)
        return carrera

    with ThreadPoolExecutor(max_workers=5) as executor:
        carreras = list(executor.map(fetch_details, carreras_basicas))

    return carreras


def save_to_json(carreras, filename="data/carreras_globaltempo.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(carreras, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    carreras = get_globaltempo_races()
    for i, carrera in enumerate(carreras, 1):
        print(f"Carrera {i}:")
        print(f"Nombre: {carrera['nombre']}")
        print(f"Fecha: {carrera['fecha']}")
        print(f"Link: {carrera['link']}")
        print(f"Resumen: {carrera['resumen']}")
        print(f"Lugar: {carrera.get('lugar', 'Desconocido')}")
        print(f"Distancias: {', '.join(carrera.get('distancias', [])) or 'No especificadas'}")
        print(f"Precios: {', '.join(carrera.get('precio', [])) or 'No especificados'}")
        print("-" * 40)

    save_to_json(carreras)

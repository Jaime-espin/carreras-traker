import requests
from bs4 import BeautifulSoup

def get_race_details(race_url):
    response = requests.get(race_url, verify=False)
    if response.status_code != 200:
        print(f"Error al cargar {race_url}: {response.status_code}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    def safe_find_text(tag, prefix):
        el = soup.find(tag, text=lambda t: t and t.startswith(prefix))
        if el:
            return el.text.replace(prefix, "").strip()
        return "No encontrado"

    # Extraer provincia
    provincia = safe_find_text("h2", "Provincia :")
    # Extraer localidad
    localidad = safe_find_text("h2", "Localidad :")
    # Extraer distancia
    distancias_raw = safe_find_text("h2", "Distancia :")
    # Extraer precio
    precios_raw = safe_find_text("h2", "PRECIO:")

    # Separar por "/" o "," o salto de línea
    import re
    distancias = re.split(r"[/,\n]+", distancias_raw) if distancias_raw else []
    distancias = [d.strip() for d in distancias if d.strip()]

    precios = re.split(r"[/,\n]+", precios_raw) if precios_raw else []
    precios = [p.strip() for p in precios if p.strip()]

   
    return {
        "lugar": provincia+', '+ localidad,
        "distancias": distancias,
        "precio": precios
    }


def get_globaltempo_races():
    # 1. Hacemos una petición HTTP a la web de carreras para obtener el contenido HTML.
    url = "https://www.global-tempo.com"
    response = requests.get(url, verify = False)
    if response.status_code != 200:
        print(f"Error al cargar la página: {response.status_code}")
        return []

    # 2. Parseamos el HTML con BeautifulSoup. Transforma ese HTML en una estructura que podemos recorrer fácilmente.
    soup = BeautifulSoup(response.text, "html.parser")

    # 3. Creamos una lista vacía para guardar las carreras
    carreras = []

    # 4. Recorremos los elementos HTML que contienen la información de cada carrera
    # Esto es un CSS selector: busca elementos con clase "event-container"

    enlaces = soup.find_all("a")

    for a in enlaces:
        div = a.find("div", class_="cuadro_inscripcion")
        if div:
            nombre = div.find("h1").text.strip() if div.find("h1") else "Sin título"
            fecha = div.find("h2").text.strip() if div.find("h2") else "Sin fecha"
            resumen = div.get_text(separator="\n").strip()  # texto completo dentro del div
            # quitamos el nombre y la fecha del resumen para dejar solo el texto extra
            resumen = resumen.replace(nombre, "").replace(fecha, "").strip()


            link = a.get("href")
            # Añadimos la URL base para hacerla absoluta
            link_completo = f"https://www.global-tempo.com/{link}"

            detalles = get_race_details(link_completo)

            carreras.append({
                "nombre": nombre,
                "fecha": fecha,
                "link": link_completo,
                "resumen": resumen,
                **detalles
            })



    return carreras

import json

def save_to_json(carreras, filename="carreras_globaltempo.json"):
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
        print(f"Precios: {', '.join(carrera.get('precios', [])) or 'No especificados'}")
        print("-" * 40)

    save_to_json(carreras)

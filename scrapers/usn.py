import requests
from bs4 import BeautifulSoup

def scrape_usn():
    url = "https://www.ultrasierranevada.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Prueba de extracción: título y algo más
    title = soup.title.string.strip()

    # Puedes inspeccionar la página y extraer cosas concretas
    # Por ejemplo, si ves que hay una clase con la fecha del evento:
    # fecha = soup.find("p", class_="alguna-clase").text.strip()

    carrera = {
        "nombre": "Ultra Sierra Nevada",
        "url": url,
        "titulo_pagina": title,
        # "fecha_evento": fecha,  # lo añadiremos cuando lo localices
    }

    return carrera

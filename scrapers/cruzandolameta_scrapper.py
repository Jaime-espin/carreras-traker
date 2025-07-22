import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.cruzandolameta.es"

def get_total_pages(soup):
    paginacion = soup.find("ul", class_="pagination")
    if not paginacion:
        return 1  # No hay paginación => solo 1 página

    max_page = 1
    enlaces = paginacion.find_all("a", class_="page-link")
    for enlace in enlaces:
        href = enlace.get("href", "")
        if "?page=" in href:
            try:
                num = int(href.split("?page=")[-1])
                if num > max_page:
                    max_page = num
            except ValueError:
                continue

    return max_page

def get_cruzandolameta_races():
    # 1. Hacemos una petición HTTP a la web de carreras para obtener el contenido HTML.
    url_base = "https://www.cruzandolameta.es/carreras/proximas/"
    response = requests.get(url_base, verify = False)
    if response.status_code != 200:
        print(f"Error al cargar la página: {response.status_code}")
        return []
     # 3. Creamos una lista vacía para guardar las carreras
    carreras = []

    # 2. Parseamos el HTML con BeautifulSoup. Transforma ese HTML en una estructura que podemos recorrer fácilmente.
    soup = BeautifulSoup(response.text, "html.parser")
    total_pages = get_total_pages(soup)
    print(f"Total páginas detectadas: {total_pages}")

    # Recorremos todas las páginas
    # Recorremos todas las páginas
    for page_num in range(1, total_pages + 1):
        print(f"Procesando página {page_num} de {total_pages}")
        if page_num == 1:
            url = url_base  # Primera página sin query ?page=1
        else:
            url = f"{url_base}?page={page_num}"

        resp = requests.get(url, verify=False)
        if resp.status_code != 200:
            print(f"Error al cargar la página {page_num}: {resp.status_code}")
            continue

        soup_page = BeautifulSoup(resp.text, "html.parser")
        bloques = soup_page.find_all("div", class_="col-md-6")

        for bloque in bloques:
            # Fecha
            fecha_div = bloque.find_previous_sibling("div", class_="col-md-2")
            fecha_completa = ""
            if fecha_div:
                date_header = fecha_div.find("div", class_="date-header")
                if date_header:
                    fecha_span = date_header.find("span")
                    if fecha_span:
                        partes = fecha_span.get_text(separator=" ").split()
                        if len(partes) == 2:
                            dia, mes = partes
                        else:
                            dia, mes = "", ""
                    else:
                        dia, mes = "", ""
                    anio = date_header.get_text(separator=" ").split()[-1]
                    fecha_completa = f"{dia} {mes} {anio}".strip()

            # Nombre y link
            h4 = bloque.find("h4") if bloque else None
            if not h4:
                continue  # Saltamos si no hay <h4>

            enlace = h4.find("a")
            if not enlace:
                continue  # Saltamos si no hay <a>

            nombre = enlace.text.strip()
            link = BASE_URL + enlace.get("href")

            # Lugar (ciudad + provincia)
            lugar = bloque.find("i", class_="fa-map-marker")
            lugar_texto = lugar.find_parent().text.strip() if lugar else "Desconocido"

            # Distancia
            distancia = bloque.find("i", class_="fa-road")
            distancia_texto = distancia.find_parent().text.strip().replace("Distancia:", "").strip() if distancia else "Desconocida"

            # Hora
            hora = bloque.find("i", class_="fa-clock-o")
            hora_texto = hora.find_parent().text.strip().replace("Hora:", "").strip() if hora else "Desconocida"

            # Tipo
            tipo = None
            for p in bloque.find_all("p", class_="data-info proximas-color"):
                if "Tipo:" in p.text:
                    tipo = p.text.replace("Tipo:", "").strip()
                    break

            carreras.append({
                "nombre": nombre,
                "fecha":fecha_completa,
                "link": link,
                "lugar": lugar_texto,
                "distancia": distancia_texto,
                "hora": hora_texto,
                "tipo": tipo if tipo else "No especificado"
                #**detalles
            })

    return carreras

import json
if __name__ == "__main__":
    carreras = get_cruzandolameta_races()
    # Guardar en JSON
    with open("carreras_cruzandolameta.json", "w", encoding="utf-8") as f:
        json.dump(carreras, f, ensure_ascii=False, indent=4)
    for i, carrera in enumerate(carreras, 1):
        print(f"Carrera {i}:")
        for k, v in carrera.items():
            print(f"{k.capitalize()}: {v}")
        print("-" * 40)
    
    
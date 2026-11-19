import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "https://www.cruzandolameta.es"


def get_total_pages(soup):
    paginacion = soup.find("ul", class_="pagination")
    if not paginacion:
        return 1

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
    url_base = "https://www.cruzandolameta.es/carreras/proximas/"
    session = requests.Session()
    try:
        response = session.get(url_base)
    except requests.exceptions.SSLError:
        print("⚠️ SSL error, reintentando sin verify...")
        response = session.get(url_base, verify=False)
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return []

    if response.status_code != 200:
        print(f"Error al cargar la página: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    total_pages = get_total_pages(soup)
    print(f"Total páginas detectadas: {total_pages}")

    carreras = []

    for page_num in range(1, total_pages + 1):
        print(f"Procesando página {page_num} de {total_pages}")
        if page_num == 1:
            url = url_base
        else:
            url = f"{url_base}?page={page_num}"

        try:
            resp = session.get(url)
        except requests.exceptions.SSLError:
            print(f"⚠️ SSL error en página {page_num}, reintentando...")
            resp = session.get(url, verify=False)
        except Exception as e:
            print(f"❌ Error en página {page_num}: {e}")
            continue

        if resp.status_code != 200:
            print(f"Error al cargar la página {page_num}: {resp.status_code}")
            continue

        soup_page = BeautifulSoup(resp.text, "html.parser")
        bloques = soup_page.find_all("div", class_="col-md-6")

        for bloque in bloques:
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

            h4 = bloque.find("h4") if bloque else None
            if not h4:
                continue

            enlace = h4.find("a")
            if not enlace:
                continue

            nombre = enlace.text.strip()
            link = urljoin(BASE_URL, enlace.get("href"))

            lugar = bloque.find("i", class_="fa-map-marker")
            lugar_texto = lugar.find_parent().text.strip() if lugar else "Desconocido"

            distancia = bloque.find("i", class_="fa-road")
            distancia_texto = distancia.find_parent().text.strip().replace("Distancia:", "").strip() if distancia else "Desconocida"

            hora = bloque.find("i", class_="fa-clock-o")
            hora_texto = hora.find_parent().text.strip().replace("Hora:", "").strip() if hora else "Desconocida"

            tipo = None
            for p in bloque.find_all("p", class_="data-info proximas-color"):
                if "Tipo:" in p.text:
                    tipo = p.text.replace("Tipo:", "").strip()
                    break

            carreras.append({
                "nombre": nombre,
                "fecha": fecha_completa,
                "link": link,
                "lugar": lugar_texto,
                "distancia": distancia_texto,
                "hora": hora_texto,
                "tipo": tipo if tipo else "No especificado",
                "fuente": "cruzandolameta"
            })

    return carreras


if __name__ == "__main__":
    carreras = get_cruzandolameta_races()
    with open("data/carreras_cruzandolameta.json", "w", encoding="utf-8") as f:
        json.dump(carreras, f, ensure_ascii=False, indent=4)
    for i, carrera in enumerate(carreras, 1):
        print(f"Carrera {i}:")
        for k, v in carrera.items():
            print(f"  {k.capitalize()}: {v}")
        print("-" * 40)

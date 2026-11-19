from bs4 import BeautifulSoup
import requests
import json

BASE_URL = "https://sportmaniacs.com/es/races"


def get_race_details(race_url):
    pass  # Implementación pendiente


def get_total_pages(soup):
    paginacion = soup.find("ul", class_="pagination")
    if not paginacion:
        return 1

    max_pages = 1  # Inicializado antes del condicional para evitar UnboundLocalError
    last_page_element = soup.find("li", class_="page-item lastPage")
    if last_page_element:
        link = last_page_element.find("a", class_="page-link")
        if link:
            try:
                max_pages = int(link.get_text(strip=True))
            except ValueError:
                print("Error al convertir el número de página")
                return 1

    return max_pages


def get_sportmaniacs_races():
    session = requests.Session()
    try:
        response = session.get(BASE_URL)
    except requests.exceptions.SSLError:
        print("⚠️ SSL error, reintentando sin verify...")
        response = session.get(BASE_URL, verify=False)
    except Exception as e:
        print(f"❌ Error al cargar la página: {e}")
        return []

    if response.status_code != 200:
        print(f"Error al cargar la página: {response.status_code}")
        return []

    carreras = []
    soup = BeautifulSoup(response.text, "html.parser")
    total_pages = get_total_pages(soup)
    print(f"Total páginas detectadas: {total_pages}")

    for page_num in range(1, total_pages + 1):
        print(f"Procesando página {page_num} de {total_pages}")
        if page_num == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}?page={page_num}"

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
        bloques = soup_page.find_all("div", class_="blockGrid-item")

        for bloque in bloques:
            carrera_data = {}

            nombre_element = bloque.find("h3", class_="card-title")
            if nombre_element:
                carrera_data["nombre"] = nombre_element.get_text(strip=True)
            else:
                print("No se encontró nombre en este bloque")
                continue

            fecha_element = bloque.find("time")
            if fecha_element:
                fecha_datetime = fecha_element.get("datetime")
                fecha_texto = fecha_element.get_text(strip=True)
                carrera_data["fecha_datetime"] = fecha_datetime
                carrera_data["fecha_texto"] = fecha_texto
            else:
                print("No se encontró fecha en este bloque")
                carrera_data["fecha_datetime"] = None
                carrera_data["fecha_texto"] = None

            carrera_data["fuente"] = "sportmaniacs"
            carreras.append(carrera_data)

    return carreras


if __name__ == "__main__":
    carreras = get_sportmaniacs_races()
    for i, carrera in enumerate(carreras, 1):
        print(f"Carrera {i}:")
        for k, v in carrera.items():
            print(f"  {k.capitalize()}: {v}")
        print("-" * 40)

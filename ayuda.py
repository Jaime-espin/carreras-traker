from bs4 import BeautifulSoup

# Ejemplo HTML simple para pruebas
html = """
<html>
  <body>
    <div class="contenedor">
      <h4><a href="/carrera1">Carrera 1</a></h4>
      <div class="date-header">
        <span>26 Julio</span> 2025
      </div>
      <p class="data-info proximas-color">Tipo: Carrera Popular</p>
      <i class="fa-map-marker"></i> Ciudad X
    </div>

    <div class="contenedor">
      <h4><a href="/carrera2">Carrera 2</a></h4>
      <div class="date-header">
        <span>15 Agosto</span> 2025
      </div>
      <p class="data-info proximas-color">Tipo: Trail</p>
      <i class="fa-map-marker"></i> Ciudad Y
    </div>
  </body>
</html>
"""

# Creamos el objeto soup
soup = BeautifulSoup(html, "html.parser")

# 1. find() — Buscar el primer div con clase "contenedor"
primer_div = soup.find("div", class_="contenedor")
print("Primer div:", primer_div)

# 2. find_all() — Buscar todos los div con clase "contenedor"
todos_los_divs = soup.find_all("div", class_="contenedor")
print("Número de divs encontrados:", len(todos_los_divs))

# 3. Extraer texto de un elemento
h4 = primer_div.find("h4")
print("Texto del h4:", h4.text.strip())

# 4. Extraer atributo href del enlace <a>
a = h4.find("a")
print("href del enlace:", a.get("href"))

# 5. Navegar por el árbol: encontrar el span dentro del div "date-header"
fecha_div = primer_div.find("div", class_="date-header")
span = fecha_div.find("span")
print("Fecha en span:", span.text.strip())

# 6. Obtener texto completo incluyendo año (que está fuera del span)
fecha_completa = fecha_div.get_text(separator=" ").strip()
print("Texto completo fecha_div:", fecha_completa)

# 7. Buscar con select() — buscar todos los p que tengan clase "data-info proximas-color"
tipos = soup.select("p.data-info.proximas-color")
for tipo in tipos:
    print("Tipo de carrera:", tipo.text.strip())

# 8. Manejo de casos donde no se encuentra el elemento (para evitar errores)
icono = primer_div.find("i", class_="fa-map-marker")
if icono:
    padre = icono.find_parent()
    lugar = padre.text.strip()
else:
    lugar = "No especificado"
print("Lugar:", lugar)

# 9. Extraer texto y limpiar espacios
tipo_p = primer_div.find("p", class_="data-info proximas-color")
tipo_texto = tipo_p.text.replace("Tipo:", "").strip() if tipo_p else "No especificado"
print("Tipo limpio:", tipo_texto)

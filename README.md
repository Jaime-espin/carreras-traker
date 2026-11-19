# 🏃 Carreras Tracker

Aplicación ligera en Python para recopilar, normalizar y consultar carreras populares, trail y eventos deportivos en España (GlobalTempo, CruzandoLaMeta, etc.).

---

## ⚡ Inicio Rápido

### 1. Requisitos
Instala las dependencias necesarias:
```bash
pip install -r requirements.txt
```

### 2. Recopilar y Normalizar Datos
Ejecuta el pipeline principal para descargar, limpiar y guardar las carreras (genera `data/carreras.json` y sincroniza la base de datos SQLite):
```bash
python main.py
```
*(Si no dispones de conexión a Internet, utilizará automáticamente la última copia local guardada).*

### 3. Iniciar la Interfaz Web
Lanza el servidor local:
```bash
python app.py
```
Abre tu navegador en: [http://localhost:5000](http://localhost:5000)

---

## 📁 Estructura del Proyecto

```
carreras-traker/
├── app.py                 # Servidor web Flask y API
├── main.py                # Pipeline principal (descarga, limpia y guarda)
├── db.py                  # Gestión unificada de SQLite (crea y sincroniza)
├── requirements.txt       # Dependencias mínimas (requests, beautifulsoup4, Flask)
├── normalizacion/
│   └── limpieza.py        # Normalizador de fechas, lugares, distancias y tipos
├── scrapers/
│   ├── cruzandolameta_scraper.py
│   ├── globaltempo_scraper.py
│   └── sportmaniacs_scraper.py
├── data/
│   ├── carreras.json      # Carreras procesadas y ordenadas por fecha
│   ├── carreras_cruzandolameta.json
│   └── carreras_globaltempo.json
├── db/
│   ├── schema.sql         # Esquema de tablas
│   └── carreras.db        # Base de datos SQLite
└── templates/
    └── index.html         # Frontend minimalista generado con IA
```

---

## ✨ Características de la Interfaz Web

> 🤖 **Nota:** El frontend ha sido generado y optimizado con Inteligencia Artificial (IA).

- **Diseño ultra simple:** Vista de tabla limpia y directa con 4 columnas esenciales (Fecha, Carrera, Lugar y Distancia).
- **Búsqueda instantánea:** Barra de búsqueda en tiempo real que filtra por nombre, lugar, tipo o distancia (ej. `10k`, `Granada`, `Trail`).
- **Enlace directo:** El nombre de la carrera lleva directamente a la página oficial de información/inscripción.
- **Sin dependencias externas:** HTML, CSS y JavaScript nativo minimalista (menos de 150 líneas en total).

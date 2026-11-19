"""
Módulo de normalización y limpieza de carreras.
Estandariza fechas, lugares (ciudad y provincia), distancias y tipos de evento.
"""

from datetime import datetime
import re
import unicodedata

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

MESES_ABREV = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def parsear_fecha(fecha_str):
    """
    Parsea una fecha en formatos comunes:
    - 'DD-MM-AAAA ...' o 'DD/MM/AAAA'
    - 'DD Mes AAAA' (ej. '09 Agosto 2025')
    - 'AAAA-MM-DD'
    Devuelve string ISO 'AAAA-MM-DD' o None.
    """
    if not fecha_str or not isinstance(fecha_str, str):
        return None
    s = fecha_str.strip()

    # Formato AAAA-MM-DD
    m_iso = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m_iso:
        y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
        try:
            return f"{y:04d}-{m:02d}-{d:02d}"
        except ValueError:
            pass

    # Formato DD-MM-AAAA o DD/MM/AAAA
    m_dmy = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", s)
    if m_dmy:
        d, m, y = int(m_dmy.group(1)), int(m_dmy.group(2)), int(m_dmy.group(3))
        try:
            return f"{y:04d}-{m:02d}-{d:02d}"
        except ValueError:
            pass

    # Formato 'DD Mes AAAA'
    m_text = re.search(r"(\d{1,2})\s+([a-zA-ZáéíóúÁÉÍÓÚ]+)\s+(\d{4})", s)
    if m_text:
        d = int(m_text.group(1))
        mes_str = m_text.group(2).lower()
        y = int(m_text.group(3))
        m = MESES.get(mes_str)
        if m:
            try:
                return f"{y:04d}-{m:02d}-{d:02d}"
            except ValueError:
                pass

    return None


def formatear_fecha_display(fecha_iso):
    """Convierte '2025-08-09' a '09 Ago 2025' para mostrar en la interfaz."""
    if not fecha_iso:
        return "Fecha por confirmar"
    try:
        y, m, d = [int(p) for p in fecha_iso.split("-")]
        mes_nombre = MESES_ABREV[m] if 1 <= m <= 12 else str(m)
        return f"{d:02d} {mes_nombre} {y}"
    except Exception:
        return fecha_iso


def parsear_lugar(lugar):
    """
    Extrae (ciudad, provincia) a partir de cadenas como:
    - 'Garrucha (Almería).' -> ('Garrucha', 'Almería')
    - 'GRANADA, PADUL' -> ('Padul', 'Granada')
    - 'GRANADA, No encontrado' -> ('Granada', 'Granada')
    """
    if not lugar or not isinstance(lugar, str):
        return "No especificada", "No especificada"

    lugar = lugar.strip().rstrip(".")

    # Formato 'Ciudad (Provincia)'
    if "(" in lugar and ")" in lugar:
        ciudad = lugar.split("(")[0].strip()
        provincia = lugar.split("(")[1].replace(")", "").strip()
        return ciudad, provincia

    # Formato 'PROVINCIA, LOCALIDAD'
    if "," in lugar:
        parts = [p.strip() for p in lugar.split(",", 1)]
        prov = parts[0].capitalize()
        ciud = parts[1].title() if parts[1].lower() not in ("no encontrado", "desconocido") else prov
        return ciud, prov

    return lugar.title(), "No especificada"


def parsear_distancias(dist_raw):
    """Extrae valores numéricos en km (float) a partir de texto o lista de distancias."""
    if not dist_raw:
        return []

    texto = " ".join(dist_raw) if isinstance(dist_raw, list) else str(dist_raw)
    if any(ign in texto.lower() for ign in ["no encontrado", "varias", "---"]):
        return []

    # Extraer patrones tipo 10 km, 7,25 Km, 10K, etc.
    matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*(?:km|k\b)?", texto, re.IGNORECASE)
    distancias = []
    for m in matches:
        try:
            km = float(m.replace(",", "."))
            # Filtrar distancias ilógicas fuera de rango carrera a pie / mtb
            if 0.5 <= km <= 350 and km not in distancias:
                distancias.append(km)
        except ValueError:
            continue

    return sorted(distancias)


def normalizar_tipo(tipo_raw, nombre="", resumen=""):
    """Clasifica la carrera en categorías claras y legibles."""
    texto = f"{tipo_raw or ''} {nombre} {resumen}".lower()

    if any(k in texto for k in ["trail", "cxm", "montaña", "montana"]):
        return "Trail / Montaña"
    if any(k in texto for k in ["triatl", "duatl", "acuát"]):
        return "Triatlón / Duatlón"
    if any(k in texto for k in ["mtb", "bici", "ciclism"]):
        return "MTB / Ciclismo"
    if any(k in texto for k in ["nado", "natac", "travesia"]):
        return "Natación"
    if any(k in texto for k in ["obstacul"]):
        return "Obstáculos"
    if any(k in texto for k in ["ruta", "asfalto", "10k", "5k", "media maraton", "maraton"]):
        return "Ruta / Asfalto"
    return "Carrera Popular"


def limpiar_carrera(carrera):
    """Limpia y estandariza una carrera individual."""
    nombre = carrera.get("nombre", "").strip()
    fecha_iso = parsear_fecha(carrera.get("fecha"))
    fecha_display = formatear_fecha_display(fecha_iso)

    ciudad, provincia = parsear_lugar(carrera.get("lugar"))

    # Extraer distancias (soportando tanto campo 'distancia' como 'distancias')
    dist_raw = carrera.get("distancias") if "distancias" in carrera else carrera.get("distancia")
    distancias_km = parsear_distancias(dist_raw)

    tipo = normalizar_tipo(
        carrera.get("tipo"),
        nombre=nombre,
        resumen=carrera.get("resumen", "")
    )

    fuente = carrera.get("fuente", "desconocido")
    # Limpiar formato de fuente para mostrar bien
    if fuente.lower() in ("globaltempo", "global-tempo"):
        fuente = "GlobalTempo"
    elif fuente.lower() in ("cruzandolameta", "cruzando la meta"):
        fuente = "CruzandoLaMeta"

    hora = carrera.get("hora")
    if hora and re.search(r"\d{1,2}:\d{2}", hora):
        m_hora = re.search(r"(\d{1,2}:\d{2})", hora)
        hora = m_hora.group(1) if m_hora else None
    else:
        hora = None

    return {
        "nombre": nombre,
        "fecha": fecha_iso,
        "fecha_display": fecha_display,
        "link": carrera.get("link", ""),
        "ciudad": ciudad,
        "provincia": provincia,
        "distancias": [{"distancia_km": d, "precio": None} for d in distancias_km],
        "distancias_km": distancias_km,
        "hora": hora,
        "tipo": tipo,
        "fuente": fuente
    }

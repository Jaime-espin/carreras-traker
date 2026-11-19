"""
Pipeline principal de carreras-tracker:
1. Obtiene las carreras de los scrapers (con soporte de respaldo local si no hay conexión).
2. Limpia y normaliza los datos (fechas, lugares, distancias, tipos).
3. Guarda el resultado unificado en data/carreras.json y actualiza la base de datos SQLite.
"""

import json
import logging
import os
import sys

from normalizacion.limpieza import limpiar_carrera
import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def cargar_cache_local(archivo, fuente):
    """Carga datos locales de respaldo si el scraper no tiene conexión."""
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
                for d in datos:
                    d.setdefault("fuente", fuente)
                logger.info(f"Cargadas {len(datos)} carreras desde respaldo local {archivo}")
                return datos
        except Exception as e:
            logger.warning(f"No se pudo leer {archivo}: {e}")
    return []


def obtener_carreras():
    carreras_gt = []
    carreras_ctm = []

    # 1. GlobalTempo
    try:
        from scrapers.globaltempo_scraper import get_globaltempo_races
        carreras_gt = get_globaltempo_races()
        if carreras_gt:
            logger.info(f"GlobalTempo: {len(carreras_gt)} carreras descargadas.")
            with open("data/carreras_globaltempo.json", "w", encoding="utf-8") as f:
                json.dump(carreras_gt, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Error ejecutando scraper GlobalTempo: {e}")

    if not carreras_gt:
        logger.info("Usando datos locales de GlobalTempo...")
        carreras_gt = cargar_cache_local("data/carreras_globaltempo.json", "GlobalTempo")

    # 2. CruzandoLaMeta
    try:
        from scrapers.cruzandolameta_scraper import get_cruzandolameta_races
        carreras_ctm = get_cruzandolameta_races()
        if carreras_ctm:
            logger.info(f"CruzandoLaMeta: {len(carreras_ctm)} carreras descargadas.")
            with open("data/carreras_cruzandolameta.json", "w", encoding="utf-8") as f:
                json.dump(carreras_ctm, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Error ejecutando scraper CruzandoLaMeta: {e}")

    if not carreras_ctm:
        logger.info("Usando datos locales de CruzandoLaMeta...")
        carreras_ctm = cargar_cache_local("data/carreras_cruzandolameta.json", "CruzandoLaMeta")

    return carreras_gt + carreras_ctm


def main():
    os.makedirs("data", exist_ok=True)
    todas_raw = obtener_carreras()

    if not todas_raw:
        logger.error("No se encontraron carreras ni en vivo ni en caché local.")
        sys.exit(1)

    # Limpiar y normalizar
    carreras_limpias = []
    for c in todas_raw:
        try:
            limpia = limpiar_carrera(c)
            carreras_limpias.append(limpia)
        except Exception as e:
            logger.warning(f"Error limpiando {c.get('nombre', 'sin nombre')}: {e}")

    # Ordenar por fecha cronológica (las que tienen fecha primero)
    carreras_limpias.sort(
        key=lambda x: (0 if x["fecha"] else 1, x["fecha"] or "9999-12-31", x["nombre"])
    )

    # Guardar en data/carreras.json
    out_file = os.path.join("data", "carreras.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(carreras_limpias, f, indent=2, ensure_ascii=False)
    logger.info(f"Guardadas {len(carreras_limpias)} carreras en {out_file}")

    # Sincronizar automáticamente la base de datos SQLite
    try:
        db.guardar_carreras(carreras_limpias)
        logger.info("Base de datos SQLite sincronizada correctamente.")
    except Exception as e:
        logger.warning(f"No se pudo sincronizar SQLite: {e}")

    con_fecha = sum(1 for c in carreras_limpias if c["fecha"])
    logger.info(f"Listo: {len(carreras_limpias)} carreras listas ({con_fecha} con fecha confirmada).")


if __name__ == "__main__":
    main()

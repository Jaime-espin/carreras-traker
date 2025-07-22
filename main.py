from scrapers.globaltempo_scraper import get_globaltempo_races
import json

if __name__ == "__main__":
    carreras = get_globaltempo_races()

    with open("data/carreras.json", "w", encoding="utf-8") as f:
        json.dump(carreras, f, ensure_ascii=False, indent=2)

    print(f"Se han guardado {len(carreras)} carreras.")

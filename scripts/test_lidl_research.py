"""Bounded read-only local retailer research: no publication or data archive."""
import sys
from pathlib import Path

def main():
    sys.path.insert(0, str(Path("/tmp/lidl-discounts")))
    from main import LidlPlus
    with LidlPlus(country="DE",latitude=48.837,longitude=10.093,timeout=20) as client:
        matches=client.search_stores("Aalen",limit=6)
        print("Lidl Filialsuche Treffer:",len(matches))
        for store in matches:
            print("Ort:",store.locality,"PLZ:",store.postal_code,"Filialkennung:",store.store_key)
        local=[s for s in matches if (s.locality or "").casefold()=="aalen" and s.store_key]
        if not local:
            raise RuntimeError("Keine eindeutig zuordenbare Lidl Filiale für Aalen")
        response=client.offers(local[0].store_key)
        print("Lidl Aalen Angebotszahl:",len(response.offers))
        if response.offers:
            item=response.offers[0]
            print("Lidl Angebotsfelder:",sorted(item.model_dump().keys()))
        if not response.offers:
            raise RuntimeError("Keine Lidl-Angebote für Aalen")
if __name__=="__main__":
    main()

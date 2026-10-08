#!/usr/bin/env python3
"""Frei lizenzierte, datierte Preisbeobachtungen. Keine Wochenangebote."""
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://prices.openfoodfacts.org/api/v1"
OUT = Path(__file__).resolve().parents[1] / "data" / "open-prices.json"
HEADERS = {"User-Agent": "AngebotsRadarAalen/1.1 (noncommercial; Open Prices attribution)", "Accept": "application/json"}

def get(path, params):
    url = BASE + path + "?" + urlencode(params)
    with urlopen(Request(url, headers=HEADERS), timeout=25) as response:
        return json.load(response)

def collect():
    stores = get("/locations/nearby", {"lat":48.837, "lon":10.093, "radius_km":20, "size":100}).get("items", [])
    today = dt.datetime.now(dt.timezone.utc).date()
    cutoff = today - dt.timedelta(days=30)
    result = []
    for store in stores:
        if not store.get("price_count"):
            continue
        if len(result) >= 250:
            break
        try:
            rows = get("/prices", {"location_id":store["id"], "date__gte":cutoff.isoformat(), "currency":"EUR", "size":100}).get("items",[])
        except Exception as exc:
            print("Einzelner Markt konnte nicht geladen werden:", store.get("id"), exc)
            continue
        for p in rows:
            date = str(p.get("date") or "")
            try:
                observed = dt.date.fromisoformat(date)
                price = float(p.get("price"))
            except (ValueError, TypeError):
                continue
            if observed < cutoff or observed > today or not (0 <= price <= 10000):
                continue
            product = p.get("product") or {}
            name = str(p.get("product_name") or product.get("product_name") or "").strip()
            if not name:
                continue
            result.append({
                "name":name[:160], "market": str(store.get("osm_name") or store.get("osm_brand") or "Markt")[:90],
                "address":str(store.get("osm_display_name") or "")[:200],
                "distance_km":store.get("distance_km"), "price":round(price,2), "date":date,
                "discount_reported": bool(p.get("price_is_discounted")),
                "source_url":"https://prices.openfoodfacts.org/prices/" + str(p.get("id")),
            })
    result.sort(key=lambda p:(p["name"].lower(),p["price"]))
    return {"source":"Open Prices / Open Food Facts","license":"ODbL 1.0","license_url":"https://opendatacommons.org/licenses/odbl/1.0/",
        "checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "note":"Preisbeobachtungen der letzten 30 Tage; keine bestätigten aktuellen Wochenangebote.",
        "items":result[:250]}

if __name__=="__main__":
    data=collect()
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"{len(data['items'])} regionale Preisbeobachtungen gespeichert.")

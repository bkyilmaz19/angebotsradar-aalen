#!/usr/bin/env python3
"""Import ALDI SÜD factual advertised sale prices from research CLI JSON.
No images, no prospect reproduction; checks validity and source URL.
Not affiliated with ALDI SÜD. Offers may vary by branch.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "offers.json"
STATUS = ROOT / "data" / "status.json"
ALDI = "https://www.aldi-sued.de"
TODAY = dt.datetime.now(ZoneInfo("Europe/Berlin")).date()

def day(s):
    return dt.date.fromisoformat(str(s)[:10])

def cents_price(raw):
    v = raw.get("amountRelevant") or raw.get("amount")
    if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
        return None
    return round(v / 100, 2)

def old_price(raw):
    val = str(raw.get("wasPriceDisplay") or "").strip()
    m = re.search(r"(\d+[,.]\d{2})", val)
    return float(m.group(1).replace(",", ".")) if m else None

def normalize(doc, today=TODAY):
    if not isinstance(doc,list):
        raise ValueError("Gruppenliste fehlt")
    out=[]
    for group in doc:
        if not isinstance(group,dict): continue
        try:
            start = day(group["date"])
            end = day(group["validUntil"])
        except (KeyError,ValueError,TypeError):
            continue
        if not (start <= today <= end): continue
        for p in group.get("products") or []:
            if not isinstance(p,dict): continue
            amount = p.get("price") or {}
            if not isinstance(amount,dict): continue
            price=cents_price(amount)
            was=old_price(amount)
            # Only offers with explicit former price, not normal shelf prices
            if price is None: continue
            if was is not None and was <= price: was = None
            name = " ".join(filter(None,[str(p.get("brandName") or "").strip(),str(p.get("name") or "").strip()]))
            sku = str(p.get("sku") or "")
            slug = str(p.get("urlSlugText") or "")
            if not name.strip() or not re.fullmatch(r"[A-Za-z0-9-]{3,100}",slug) or not re.fullmatch(r"[0-9]{4,30}",sku):continue
            out.append({
                "id":f"aldi-{sku}-{start.isoformat()}",
                "name":name[:180], "market":"ALDI SÜD", "city":"Aalen",
                "category": "ALDI Wochenangebot",
                "quantity":str(p.get("sellingSize") or "")[:100],
                "price":price, "old_price":was, "valid_from":start.isoformat(),
                "valid_until":end.isoformat(),
                "source_url":f"{ALDI}/produkt/{slug}-{sku}",
                "branch":"Regionale Verfügbarkeit vor Einkauf prüfen",
                "reference_price":str(amount.get("comparisonDisplay") or "")[:80],
            })
    return list({p["id"]:p for p in out}.values())

def main(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    offers=normalize(data)
    if not offers:
        raise RuntimeError("Keine derzeit gültigen ALDI-Angebotsprodukte gefunden – keine Live-Daten überschreiben")
    OUT.write_text(json.dumps(offers,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    STATUS.write_text(json.dumps({"last_success_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "offer_count":len(offers),"source":"ALDI SÜD / inoffizielle öffentliche API; Filialpreise prüfen",
        "disclaimer":"Kein offizieller ALDI-Datenpartner. Gültigkeit beim Händler prüfen."},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Importierte aktuelle ALDI-Angebotsprodukte:",len(offers))

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("Usage: import_aldi.py /tmp/offers.json")
    main(sys.argv[1])

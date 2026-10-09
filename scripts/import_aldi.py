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

def category_for(name, categories=None):
    """Grobe Sortierung für Filter. Bei Unsicherheit keine Lebensmittel behaupten."""
    text = " ".join([str(name)] + [str(c.get("name", "")) for c in (categories or []) if isinstance(c, dict)]).casefold()
    # Explizite Nonfood-Signale haben Vorrang: z. B. Schokolade als
    # Hosenfarbe oder Kaffee im Namen eines Holz-Spielsets.
    groups = (
        ("Kleidung & Schuhe", ("schuhe", "boots", "stiefel", "socken", "jacke", "hose", "shirt", "pullover", "bekleidung", "haarreif")),
        ("Haushalt & Freizeit", ("haushalt", "küche", "werkzeug", "spielzeug", "spielset", "spielküche", "puppen", "plüschtier", "baustein", "toylino", "holz-gebäck", "garten", "lampe", "deko", "halloween")),
        ("Milchprodukte & Eier", ("milch", "joghurt", "butter", "quark", "käse", "mozzarella", "frischkäse", "skyr", "eier")),
        ("Obst & Gemüse", ("obst", "gemüse", "banane", "äpfel", "apfel", "tomate", "gurke", "salat", "kartoffel", "trauben")),
        ("Brot & Backwaren", ("brot", "brötchen", "baguette", "toast", "croissant", "backwaren")),
        ("Fleisch & Fisch", ("fleisch", "hähnchen", "wurst", "schinken", "lachs", "fisch", "steak")),
        ("Getränke", ("kaffee", "espresso", "tee", "saft", "getränk", "mineralwasser", "limonade")),
        ("Lebensmittel & Vorrat", ("nudel", "pasta", "reis", "müsli", "mehl", "zucker", "schokolade", "keks", "pizza", "öl", "konserve")),
    )
    for group, terms in groups:
        if any(word in text for word in terms):
            return group
    return "Weitere Angebote"

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
            # Angebotsartikel können auch ohne durchgestrichenen Altpreis vorkommen.
            if price is None: continue
            if was is not None and was <= price: was = None
            name = " ".join(filter(None,[str(p.get("brandName") or "").strip(),str(p.get("name") or "").strip()]))
            sku = str(p.get("sku") or "")
            slug = str(p.get("urlSlugText") or "")
            if not name.strip() or not re.fullmatch(r"[A-Za-z0-9-]{3,100}",slug) or not re.fullmatch(r"[0-9]{4,30}",sku):continue
            out.append({
                "id":f"aldi-{sku}-{start.isoformat()}",
                "name":name[:180], "market":"ALDI SÜD", "city":"Aalen",
                "category": category_for(name, p.get("categories")),
                "quantity":str(p.get("sellingSize") or "")[:100],
                "price":price, "old_price":was, "valid_from":start.isoformat(),
                "valid_until":end.isoformat(),
                "source_url":f"{ALDI}/produkt/{slug}-{sku}",
                "branch":"Regionale Verfügbarkeit vor Einkauf prüfen",
                "reference_price":str(amount.get("comparisonDisplay") or "")[:80],
            })
    unique = {}
    for p in out:
        existing = unique.get(p["id"])
        if existing is None or (p["old_price"] is not None and existing["old_price"] is None):
            unique[p["id"]] = p
    return list(unique.values())

def main(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    offers=normalize(data)
    if not offers:
        raise RuntimeError("Keine derzeit gültigen ALDI-Angebotsprodukte gefunden – keine Live-Daten überschreiben")
    # Beim ALDI-Update bleiben geprüfte Angebote anderer Händler erhalten.
    existing = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    if not isinstance(existing, list):
        existing = []
    others = [o for o in existing if isinstance(o,dict)
              and o.get("market") != "ALDI SÜD"
              and str(o.get("valid_from","")) <= TODAY.isoformat() <= str(o.get("valid_until",""))]
    offers = others + offers
    OUT.write_text(json.dumps(offers,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    STATUS.write_text(json.dumps({"last_success_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "offer_count":len(offers),"source":"ALDI SÜD / inoffizielle öffentliche API; Filialpreise prüfen",
        "disclaimer":"Kein offizieller ALDI-Datenpartner. Gültigkeit beim Händler prüfen."},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Importierte aktuelle ALDI-Angebotsprodukte:",len(offers))

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("Usage: import_aldi.py /tmp/offers.json")
    main(sys.argv[1])

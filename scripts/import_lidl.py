#!/usr/bin/env python3
"""Import factual Lidl price notices for Aalen; no product photos or copied descriptions.

Read-only small-volume Lidl query through the independent Apache-2.0 client.
Not affiliated with Lidl; store and loyalty conditions must be checked on Lidl.de.
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
TODAY = dt.datetime.now(ZoneInfo("Europe/Berlin")).date()

def money(value):
    if not isinstance(value, str):
        return None
    text = value.strip().replace("\u00a0", " ")
    match = re.fullmatch(r"(?:€\s*)?(\d{1,4}(?:[.,]\d{1,2})?)(?:\s*€)?", text)
    if not match:
        return None
    amount = float(match.group(1).replace(",", "."))
    return round(amount, 2) if 0 < amount < 10000 else None

def normalize(records, today=TODAY):
    if not isinstance(records,list):
        raise ValueError("Lidl-Antwort muss eine Liste sein")
    offers={}
    for entry in records:
        if not isinstance(entry,dict): continue
        store=entry.get("store") or {}
        store_key=str(store.get("store_key") or "")
        postcode=str(store.get("postal_code") or "")
        if (store.get("locality") or "").casefold()!="aalen" or not postcode.startswith("734") or not re.fullmatch(r"DE\d{4,6}",store_key):
            continue
        for item in entry.get("offers") or []:
            if not isinstance(item,dict): continue
            try:
                start=dt.date.fromisoformat(str(item.get("start_validity_date") or "")[:10])
                end=dt.date.fromisoformat(str(item.get("end_validity_date") or "")[:10])
            except ValueError: continue
            if not start<=today<=end: continue
            name=" ".join(str(v).strip() for v in (item.get("brand"),item.get("title")) if v).strip()
            price=money(item.get("price") or "")
            if not name or price is None: continue
            raw_id=str(item.get("id") or "")
            if not re.fullmatch(r"[A-Za-z0-9_-]{2,100}",raw_id):continue
            ident=f"lidl-{store_key}-{raw_id}-{start.isoformat()}"
            offers[ident]={
                "id":ident, "name":name[:180], "market":"Lidl", "city":"Aalen",
                "category":str(item.get("category") or "Lidl Wochenangebot")[:80],
                "quantity":str(item.get("packaging") or "")[:100],
                "price":price,"old_price":None,
                "valid_from":start.isoformat(),"valid_until":end.isoformat(),
                "source_url":"https://www.lidl.de/c/online-prospekte/s10005610/",
                "branch":f"Lidl {postcode} Aalen ({store_key}); Lidl-Plus-Bedingungen prüfen",
                "reference_price":str(item.get("price_per_unit") or "")[:80],
            }
    return list(offers.values())

def collect():
    sys.path.insert(0,str(Path("/tmp/lidl-discounts")))
    from main import LidlPlus
    with LidlPlus(country="DE",latitude=48.837,longitude=10.093,timeout=20) as client:
        matches=client.search_stores("Aalen",limit=10)
        local=[s for s in matches if (s.locality or "").casefold()=="aalen"
               and (s.postal_code or "").startswith("734") and s.store_key]
        if not local:raise RuntimeError("Keine Lidl-Filiale in Aalen gefunden")
        # Maximal drei Filialen / drei Angebotsanfragen pro Lauf.
        return [{"store":s.model_dump(),"offers":[dict(o.model_dump(),price=o.price,old_price=o.old_price)
                for o in client.offers(s.store_key).offers]} for s in local[:3]]

def main():
    incoming=collect()
    fresh=normalize(incoming)
    if not fresh:raise RuntimeError("Keine verifizierbaren aktuell gültigen Lidl-Angebote, Bestand bleibt")
    existing=json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    if not isinstance(existing,list): existing=[]
    existing=[o for o in existing if isinstance(o,dict) and o.get("market")!="Lidl"
              and str(o.get("valid_from",""))<=TODAY.isoformat()<=str(o.get("valid_until",""))]
    all_offers=existing+fresh
    OUT.write_text(json.dumps(all_offers,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    STATUS.write_text(json.dumps({"last_success_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
      "offer_count":len(all_offers),"source":"ALDI SÜD und Lidl (inoffizielle öffentliche Endpunkte)",
      "disclaimer":"Kein offizieller Datenpartner; Preise, Filialen und Lidl-Plus-Bedingungen beim Händler prüfen."},
      ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Lidl-Angebote aktualisiert:",len(fresh),"Gesamt:",len(all_offers))

if __name__=="__main__":main()

#!/usr/bin/env python3
"""Import approved JSON offer feeds. No unauthorized scraping or guessed prices."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo
import urllib.request
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'data' / 'offers.json'
STATUS = ROOT / 'data' / 'status.json'
CITIES = {'Aalen', 'Essingen', 'Oberkochen', 'Abtsgmünd', 'Westhausen', 'Heubach', 'Ellwangen', 'Neresheim'}

def parse_offer(raw, today):
    if not isinstance(raw, dict):
        return None
    try:
        name = str(raw['name']).strip()
        market = str(raw['market']).strip()
        city = str(raw['city']).strip()
        price = float(raw['price'])
        start = str(raw['valid_from'])
        end = str(raw['valid_until'])
        start_date = dt.date.fromisoformat(start)
        end_date = dt.date.fromisoformat(end)
        source = str(raw['source_url']).strip()
        url = urlparse(source)
        if not name or not market or city not in CITIES or price < 0 or not (start_date <= today <= end_date) or url.scheme != 'https' or not url.hostname:
            return None
        old = raw.get('old_price')
        old = float(old) if old not in (None, '') else None
        if old is not None and old < price:
            old = None
        ident = str(raw.get('id') or hashlib.sha256(f'{market}|{city}|{name}|{start}|{end}|{price}'.encode()).hexdigest()[:20])
        return {'id': ident, 'name': name[:180], 'market': market[:90], 'city': city,
                'category': str(raw.get('category') or 'Sonstiges')[:80],
                'quantity': str(raw.get('quantity') or '')[:100], 'price': price, 'old_price': old,
                'valid_from': start, 'valid_until': end, 'source_url': source,
                'branch': str(raw.get('branch') or '')[:180],
                'reference_price': str(raw.get('reference_price') or '')[:80]}
    except (KeyError, TypeError, ValueError, OverflowError):
        return None

def load(url, key):
    if url.startswith('file://'):
        raise ValueError('file:// not allowed for remote feed')
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname:
        raise ValueError('FEED_URL must be an HTTPS address')
    headers = {'Accept': 'application/json', 'User-Agent': 'AngebotsRadarAalen/1.0'}
    if key:
        headers['Authorization'] = 'Bearer ' + key
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = response.read(10_000_001)
    if len(payload) > 10_000_000:
        raise ValueError('Feed exceeds 10MB')
    doc = json.loads(payload)
    if isinstance(doc, dict):
        doc = doc.get('offers')
    if not isinstance(doc, list):
        raise ValueError('Feed must be an array or {"offers": [...]}')
    return doc

def main():
    url = os.getenv('FEED_URL', '').strip()
    if not url:
        print('FEED_URL missing. Nothing imported; previous data unchanged.', file=sys.stderr)
        return 2
    now = dt.datetime.now(dt.timezone.utc)
    today = dt.datetime.now(ZoneInfo('Europe/Berlin')).date()
    try:
        incoming = load(url, os.getenv('FEED_API_KEY', ''))
        offers = [o for item in incoming if (o := parse_offer(item, today))]
        if incoming and not offers:
            raise ValueError('No acceptable regional, currently valid offers found; refusing replacement')
        unique = {o['id']: o for o in offers}
        result = sorted(unique.values(), key=lambda x: (x['market'], x['name'], x['city']))
        # Vorhandene ALDI-Angebote erhalten und Feed-Händler gezielt ersetzen.
        existing = json.loads(TARGET.read_text(encoding='utf-8')) if TARGET.exists() else []
        if not isinstance(existing, list):
            existing = []
        source_markets = {o['market'] for o in result}
        untouched = [o for o in existing if isinstance(o, dict)
                     and o.get('market') not in source_markets
                     and str(o.get('valid_from', '')) <= today.isoformat() <= str(o.get('valid_until', ''))]
        result = sorted(untouched + result, key=lambda x: (x['market'], x['name'], x['city']))
        TARGET.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        STATUS.write_text(json.dumps({'last_success_utc': now.isoformat(timespec='seconds'), 'offer_count':len(result),'source':'Autorisierter Angebotsfeed'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'Import successful: {len(result)} valid offers ({len(incoming)} input)')
        return 0
    except Exception as e:
        print(f'Import failed, existing offers preserved: {e}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())

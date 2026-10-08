# AngebotsRadar Aalen – deploybare Web-App

Responsive, deutschsprachige Angebotssuche mit Produktnamen, Supermarkt, Ort, Kategorie, Sortierung, Preis, Rabatt, Gültigkeit und Quellenlink.

## Schnell starten

```bash
cd aalen-angebote
python3 -m http.server 8080
```

Danach `http://localhost:8080` öffnen. Ohne echte Daten erscheint **deutlich gekennzeichnete Demo**, keine behaupteten aktuellen Preise.

## Öffentlich online schalten

Den Ordner als statische Website bei Netlify, Cloudflare Pages oder Vercel hochladen (Publish Directory: Projektwurzel, kein Build nötig). Für eine öffentliche Adresse / eigene Domain ist Zugang zu einem Hosting-Account nötig. Die Seite allein ist nach dem Upload öffentlich, aber echte Angebote benötigen eine Datenquelle.

## Echte aktuelle Angebote – Option A: JSON-Feed

1. `data/offers.json` mit validierten Angebotsdaten nach dem Schema von `data/offers.example.json` befüllen.
2. `window.APP_CONFIG.showDemoOnEmpty` auf `false` setzen.
3. Neu veröffentlichen. Nur Datensätze zwischen `valid_from` und `valid_until` werden gezeigt (nach Browserdatum).
4. Daten mindestens täglich pflegen oder automatisiert per autorisierter Schnittstelle erzeugen.

## Echte aktuelle Angebote – Option B: Zentrale Datenbank (empfohlen)

1. Kostenloses oder kostenpflichtiges Supabase-Projekt erstellen.
2. `schema.sql` im SQL Editor ausführen.
3. In `config.js` die **öffentliche** `supabaseUrl` und den **öffentlichen** `supabaseAnonKey` setzen. Niemals service_role oder Datenbankpasswörter im Frontend nutzen.
4. `showDemoOnEmpty: false` setzen und Website deployen.
5. Angebote per Supabase Dashboard oder separatem, gesichertem Import-Job einpflegen. Jedes Angebot braucht eindeutige `id`, Produkt, Händler, Ort, Preis, Start und Ende, sinnvollerweise Quelle und Filiale.

## Wichtige Daten- und Rechtsfragen

- Es gibt keine hier integrierte, nachgewiesen frei zugängliche und vollständige Angebots-API für alle Händler rund um Aalen. Von Prospekt-Plattformen nicht ohne Erlaubnis scrapen oder Inhalte/Fotos übernehmen.
- Eine Datenvereinbarung bzw. eine lizensierte Feed-Anbindung ist nötig, um die gewünschte flächendeckende, automatisierte Aktualität zu erreichen. Händler unterscheiden nach Filiale und Zeitraum.
- Rechtliche Pflichtangaben vor öffentlichem Betrieb klären: Impressum, Datenschutzerklärung, Nutzungs-/Lizenzbedingungen, Bildrechte, ggf. Grundpreisangaben und Wettbewerbsrecht. Kontakt-Platzhalter im Footer ersetzen.
- Beispieldaten in `app.js` sind ausschließlich zur Vorschau erfunden und werden **nie** als verifizierte Angebote ausgegeben.
- Grundpreis, Verfügbarkeit, Crawler, Geo-Radius und Adminoberfläche sind sinnvolle nächste Erweiterungen.

## Automatische Aktualisierung (neu)

Die Web-App ist jetzt standardmäßig im **Echt-Daten-Modus ohne Demoangebote**. Die Seite zeigt noch keine echten Angebote, bevor ein legitimer Feed konfiguriert ist.

### Öffentlich veröffentlichen über GitHub Pages

1. Kostenloses GitHub-Konto nutzen, neues **öffentliches** Repository mit Namen `angebotsradar-aalen` erstellen.
2. **Den Inhalt dieses Projektordners** (nicht nur die ZIP-Datei) im Stammverzeichnis auf `main` hochladen, einschließlich `.github/workflows/` und `.nojekyll`.
3. Repository → **Settings → Pages → Build and deployment → Source: GitHub Actions** auswählen. **Nicht** „Deploy from a branch“ verwenden, denn die bereitgestellte `deploy-pages.yml` veröffentlicht auch nach automatischen Importen zuverlässig neu.
4. Unter **Actions** nachsehen, ob „Webseite veröffentlichen“ erfolgreich durchläuft. Die URL steht in **Settings → Pages** und hat typischerweise die Form `https://BENUTZERNAME.github.io/angebotsradar-aalen/`.
5. Ohne Feed bleibt die Seite öffentlich erreichbar und zeigt transparent **noch keine aktuellen Angebote**.

### Automatische Aktualisierung (sobald ein lizenzierter Feed vorliegt)

1. Repository → **Settings → Secrets and variables → Actions** → `New repository secret`:
   - `FEED_URL`: HTTPS-Adresse des **rechtmäßig nutzbaren JSON-Feeds**.
   - `FEED_API_KEY`: optionales geheimes Zugriffstoken.
2. Im Tab **Actions → Angebote täglich aktualisieren → Run workflow** manuell anstoßen.
3. Der Workflow läuft danach für **06:17 und 18:17 Uhr Europe/Berlin** (GitHub kann verzögern). Danach startet automatisch der Workflow „Webseite veröffentlichen“.
4. `data/status.json` und die Anzeige „Letzter Import“ prüfen.

**Wichtig:** `FEED_URL` existiert noch nicht, es gibt noch keine eingebundene Live-Datenquelle. Ohne `FEED_URL` bricht der Import bewusst ab, statt Angebote zu erfinden. Alte Daten bleiben erhalten; abgelaufene Angebote werden im Browser ausgeblendet. Datenschutz, Anbieter-Lizenzen und mögliche Impressumspflichten vor dem öffentlichen Betrieb prüfen.

### Feed-Schema

Der Feed liefert ein JSON-Array oder `{ "offers": [...] }`. Beispiel:

```json
[
  {
    "id": "anbieter-12345",
    "name": "Butter",
    "market": "REWE",
    "city": "Aalen",
    "branch": "Beispiel-Filiale",
    "category": "Molkerei",
    "quantity": "250 g",
    "price": 1.49,
    "old_price": 2.29,
    "reference_price": "5,96 €/kg",
    "valid_from": "2026-10-08",
    "valid_until": "2026-10-11",
    "source_url": "https://anbieter.example/angebot/12345"
  }
]
```

**Alle Werte sind Schema-Beispiele, keine echten Angebote.** Pflichtfelder: `name`, `market`, `city`, `price`, `valid_from`, `valid_until`, `source_url`. Nur die in `scripts/update_offers.py` erlaubten Orte werden importiert. Ein regionsübergreifender Feed muss vom Anbieter bereits die echten Angebote den Orten zuordnen. Ohne Filialangaben kann nicht behauptet werden, dass ein bestimmter Markt das Angebot führt. Einen zugeschnittenen Adapter für das tatsächliche Format des lizenzierten Anbieters kann man ergänzen.

### Testen

```bash
python3 -m unittest discover -s tests -v
node --check app.js
```

**Wichtig:** Die neue Automatisierung ist vorbereitet, aber nicht aktiviert oder online gestellt. Zugang zu GitHub/Hosting und rechtmäßigem Datenfeed ist noch erforderlich. Die ZIP enthält keine echten Live-Preise. Keine nicht autorisierten Fremdseiten scrapen.

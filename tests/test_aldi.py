import datetime as dt
import unittest
from scripts.import_aldi import normalize, category_for

class AldiImportTests(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(category_for("Deutsche Markenbutter"), "Milchprodukte & Eier")
        self.assertEqual(category_for("CRANE Trekking Boots"), "Kleidung & Schuhe")
        self.assertEqual(category_for("Unbekannter Artikel"), "Weitere Angebote")
        self.assertEqual(category_for("Bio Artikel", [{"name": "Obst & Gemüse"}]), "Obst & Gemüse")


    def test_nonfood_wins_over_food_words(self):
        # Regressionen aus echten, falsch eingeordneten ALDI-Angeboten.
        self.assertEqual(
            category_for("UP2FASHION WOMEN Damen Lounge-Hose, Schokolade, S 36/38"),
            "Kleidung & Schuhe",
        )
        self.assertEqual(
            category_for("TOYLINO Holz-Gebäck-Set, Kaffee und Kuchen"),
            "Haushalt & Freizeit",
        )
        self.assertEqual(
            category_for("Spielzeug-Kaffeemaschine"),
            "Haushalt & Freizeit",
        )
        self.assertEqual(
            category_for("T-Shirt Schokolade"),
            "Kleidung & Schuhe",
        )
        self.assertEqual(
            category_for("Kerze mit Kaffeeduft"),
            "Haushalt & Freizeit",
        )

    def test_food_categories_still_work(self):
        self.assertEqual(category_for("Kaffee ganze Bohne"), "Getränke")
        self.assertEqual(category_for("Schokolade 100 g"), "Lebensmittel & Vorrat")
        self.assertEqual(category_for("Vollmilch 1 l"), "Milchprodukte & Eier")
        self.assertEqual(category_for("Baguette"), "Brot & Backwaren")

    def test_no_unverified_discount_without_old_price(self):
        today = dt.date(2026, 10, 8)
        product = {
            "name": "Schokolade", "sku": "000000019999",
            "urlSlugText": "schokolade", "price": {"amountRelevant": 199},
        }
        data = [{"date": "2026-10-05", "validUntil": "2026-10-10", "products": [product]}]
        offers = normalize(data, today)
        self.assertEqual(len(offers), 1)
        self.assertEqual(offers[0]["price"], 1.99)
        self.assertIsNone(offers[0]["old_price"])


    def test_only_explicit_active_discounts(self):
        today=dt.date(2026,10,8)
        def p(was):
            return {"name":"Milch 1l","brandName":"MILSANI","sku":"000000019999",
                    "urlSlugText":"milch-1-l","price":{"amountRelevant":99,"wasPriceDisplay":was,"comparisonDisplay":"0,99 €/1 l"}}
        doc=[{"date":"2026-10-05T00:00:00Z","validUntil":"2026-10-10T00:00:00Z","products":[p("1,49 €"),p("")]},
             {"date":"2026-10-11T00:00:00Z","validUntil":"2026-10-17T00:00:00Z","products":[p("1,49 €")]}]
        got=normalize(doc,today)
        self.assertEqual(len(got),1)
        self.assertEqual(got[0]["price"],0.99)
        self.assertEqual(got[0]["old_price"],1.49)
        self.assertEqual(got[0]["valid_until"],"2026-10-10")
        self.assertTrue(got[0]["source_url"].startswith("https://www.aldi-sued.de/produkt/"))

if __name__=="__main__": unittest.main()

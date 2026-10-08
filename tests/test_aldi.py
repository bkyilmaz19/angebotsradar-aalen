import datetime as dt
import unittest
from scripts.import_aldi import normalize

class AldiImportTests(unittest.TestCase):
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

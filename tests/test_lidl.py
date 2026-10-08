import datetime as dt
import unittest
from scripts.import_lidl import money,normalize

class LidlTests(unittest.TestCase):
    def test_prices(self):
        self.assertEqual(money("1,49 €"),1.49)
        self.assertEqual(money("0.99 €"),0.99)
        self.assertIsNone(money("1,49 €/kg"))
        self.assertIsNone(money("-"))
    def test_local_valid_offers(self):
        today=dt.date(2026,10,8)
        item={"id":"sample123","brand":"TEST","title":"Milch","price":"0,99 €",
              "old_price":"1,29 €","start_validity_date":"2026-10-05",
              "end_validity_date":"2026-10-10","category":"Lebensmittel"}
        s={"store":{"locality":"Aalen","postal_code":"73431","store_key":"DE4918"},"offers":[item]}
        self.assertEqual(len(normalize([s],today)),1)
        self.assertEqual(normalize([s],today)[0]["old_price"],1.29)
        self.assertEqual(len(normalize([dict(s,store=dict(s["store"],locality="Ahlen"))],today)),0)
        self.assertEqual(len(normalize([s],dt.date(2026,10,11))),0)
if __name__=="__main__":unittest.main()

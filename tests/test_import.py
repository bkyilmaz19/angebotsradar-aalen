import datetime as dt
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from update_offers import parse_offer

class ImportTests(unittest.TestCase):
    def setUp(self):
        self.today = dt.date(2026, 10, 8)
        self.offer = dict(name='Butter', market='REWE', city='Aalen', price=1.29,
            valid_from='2026-10-05', valid_until='2026-10-11', source_url='https://example.org/angebot')
    def test_valid(self):
        self.assertEqual(parse_offer(self.offer, self.today)['price'], 1.29)
    def test_expired(self):
        self.assertIsNone(parse_offer(dict(self.offer, valid_until='2026-10-07'), self.today))
    def test_wrong_city(self):
        self.assertIsNone(parse_offer(dict(self.offer, city='Berlin'), self.today))
    def test_no_source(self):
        self.assertIsNone(parse_offer(dict(self.offer, source_url='http://example.org'), self.today))
    def test_negative_price(self):
        self.assertIsNone(parse_offer(dict(self.offer, price=-1), self.today))
if __name__ == '__main__': unittest.main()

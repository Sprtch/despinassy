import unittest
from despinassy import db, Part, Inventory
import sqlalchemy

class TestDatabase(unittest.TestCase):
    def setUp(self):
        db.init_app(config={
            'uri': 'sqlite://',
        })
        db.drop_all()
        db.create_all()

    def test_csv_import(self):
        self.assertEqual(Part.query.count(), 0)
        Part.import_csv("./TestCSV.csv")

if __name__ == '__main__':
    unittest.main()

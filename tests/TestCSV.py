import unittest
from despinassy import db, Part, Inventory
import sqlalchemy
import io

class TestDatabase(unittest.TestCase):
    def setUp(self):
        db.init_app(config={
            'uri': 'sqlite://',
        })
        db.drop_all()
        db.create_all()

    def test_csv_import_1(self):
        self.assertEqual(Part.query.count(), 0)
        csv = io.StringIO("barcode,default_code\n1234awe134,first\n23456fewww32,second\n")
        Part.import_csv("./TestCSV.csv", { "barcode": "barcode", "default_code": "name"})

    def test_csv_import_2(self):
        self.assertEqual(Part.query.count(), 0)
        csv = io.StringIO("barcode,name\n1234awe134,first\n23456fewww32,second\n")
        Part._import_csv_content(csv)
        self.assertEqual(Part.query.count(), 2)

if __name__ == '__main__':
    unittest.main()

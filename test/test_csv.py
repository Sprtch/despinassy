import unittest
from despinassy import db, Part, Inventory
import sqlalchemy
import io
import uuid

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db.init_app(config={
            'uri': 'sqlite://',
        })

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def test_csv_import_1(self):
        """
        Test to import a CSV file in the DB
        """
        self.assertEqual(Part.query.count(), 0)
        csv = io.StringIO("name,barcode\nhello,world\nfoo,bar\n123,456\n")
        filename = "/tmp/%s" % (uuid.uuid4())
        with open(filename, "w") as f:
            print(csv.getvalue(), file=f)
        Part.import_csv(filename)
        self.assertEqual(Part.query.count(), 3)
        p = Part.query.filter(Part.barcode == "bar").first()
        self.assertEqual(p.name, "foo")
        self.assertEqual(p.barcode, "bar")
        p = Part.query.filter(Part.barcode == "world").first()
        self.assertEqual(p.name, "hello")
        self.assertEqual(p.barcode, "world")
        p = Part.query.filter(Part.barcode == "456").first()
        self.assertEqual(p.name, "123")
        self.assertEqual(p.barcode, "456")

    def test_csv_import_2(self):
        """
        Test to import a CSV StringIO in the DB
        """
        self.assertEqual(Part.query.count(), 0)
        csv = io.StringIO("default_name,barcode\nhello,world\nfoo,bar\n123,456\n")
        Part._import_csv_content(csv, {"default_name": "name", "barcode": "barcode"})
        self.assertEqual(Part.query.count(), 3)
        p = Part.query.filter(Part.barcode == "bar").first()
        self.assertEqual(p.name, "foo")
        self.assertEqual(p.barcode, "bar")
        p = Part.query.filter(Part.barcode == "world").first()
        self.assertEqual(p.name, "hello")
        self.assertEqual(p.barcode, "world")
        p = Part.query.filter(Part.barcode == "456").first()
        self.assertEqual(p.name, "123")
        self.assertEqual(p.barcode, "456")

if __name__ == '__main__':
    unittest.main()

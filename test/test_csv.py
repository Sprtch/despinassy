import unittest
from despinassy import db, Part, Inventory
import sqlalchemy
import io
import uuid

class TestCsv(unittest.TestCase):
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

    def test_csv_import_3(self):
        """
        Test the import doesn't fail when importing the same data and erase the data
        """
        self.assertEqual(Part.query.count(), 0)
        csv_content = "name,barcode\nhello,world\nfoo,bar\n123,456\n"
        Part._import_csv_content(io.StringIO(csv_content))
        self.assertEqual(Part.query.count(), 3)
        csv_content = "name,barcode\nfoo,bar\n123,456\nfoo2,bar2\n324,561\n"
        Part._import_csv_content(io.StringIO(csv_content))
        self.assertEqual(Part.query.count(), 4)
        p = Part.query.filter(Part.barcode == "world")
        self.assertEqual(p.count(), 0)

    def test_csv_import_4(self):
        """
        Test the import of file with empty field that should be passed
        """
        self.assertEqual(Part.query.count(), 0)
        csv = io.StringIO("name,barcode\nhello,world\nfoo,\n,456\n,433,\nfoo,bar\n")
        Part._import_csv_content(csv)
        self.assertEqual(Part.query.count(), 2)

    def test_csv_export_1(self):
        BARCODE = "QWERTY1234"
        NAME = "BARCODE"
        p = Part(name=NAME, barcode=BARCODE)
        db.session.add(p)
        i = Inventory(part=p)
        db.session.add(i)
        db.session.commit()
        
        self.assertEqual(Inventory.query.count(), 1)
        output = Inventory._export_csv().getvalue().strip()
        self.assertEqual(len(output.split("\n")), 2)
        header, content = output.split("\n")
        self.assertEqual(header, "id,part_name,part_barcode,quantity,created_at,updated_at")
        self.assertTrue("BARCODE,QWERTY1234,0," in content)

if __name__ == '__main__':
    unittest.main()
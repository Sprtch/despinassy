import unittest
from despinassy import db, Part, Inventory
import sqlalchemy
import io
import uuid


class TestCsv(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db.init_app(
            config={
                "uri": "sqlite://",
            }
        )

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

    def test_csv_import_with_csv_map_1(self):
        """
        Test to import a CSV StringIO in the DB
        """
        self.assertEqual(Part.query.count(), 0)
        csv = io.StringIO("default_name,barcode\nhello,world\nfoo,bar\n123,456\n")
        Part._import_csv_content(csv, {"name": "default_name", "barcode": "barcode"})
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

    def test_csv_import_with_csv_map_2(self):
        """
        Test to import a CSV StringIO in the DB with a CSV map
        """
        self.assertEqual(Part.query.count(), 0)
        csv = io.StringIO(
            '"Référence interne","Code Barre"\n"hello","world"\n"foo","bar"\n"123","456"\n'
        )
        Part._import_csv_content(
            csv, {"name": "Référence interne", "barcode": "Code Barre"}
        )
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
        self.assertEqual(Part.query.filter(Part.hidden == False).count(), 4)

    def test_csv_import_4(self):
        """
        Test the import of file with empty field that should be passed
        """
        self.assertEqual(Part.query.count(), 0)
        csv = io.StringIO("name,barcode\nhello,world\nfoo,\n,456\n,433,\nfoo,bar\n")
        Part._import_csv_content(csv)
        self.assertEqual(Part.query.count(), 2)

    def test_csv_import_latin_char(self):
        self.assertEqual(Part.query.count(), 0)
        name = "hèllô"
        barcode = "wèrld"
        csv = io.StringIO(("name,barcode\n%s,%s\n" % (name, barcode)))

        filename = "/tmp/%s" % (uuid.uuid4())
        with open(filename, "wb") as f:
            f.write(csv.getvalue().encode("latin1"))

        Part.import_csv(filename)
        self.assertEqual(Part.query.count(), 1)
        p = Part.query.get(1)
        self.assertEqual(p.name, name)
        self.assertEqual(p.barcode, barcode)

    def test_csv_re_import(self):
        """
        Test to import a CSV StringIO in the DB
        """
        self.assertEqual(Part.query.count(), 0)
        csv1 = io.StringIO("name,barcode\nhello,world\nfoo,bar\n123,456\n")
        Part._import_csv_content(csv1)
        self.assertEqual(Part.query.count(), 3)
        csv2 = io.StringIO("name,barcode\nhello,world\nfoo,bar\n")
        Part._import_csv_content(csv2)
        self.assertEqual(Part.query.filter(Part.hidden == False).count(), 2)
        self.assertEqual(Part.query.count(), 3)

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
        self.assertEqual(
            header, "id,part_name,part_barcode,quantity,created_at,updated_at"
        )
        self.assertTrue("BARCODE,QWERTY1234,0.0," in content)

    def test_csv_export_2(self):
        BARCODE = "QWERTY1234"
        NAME = "BARCODE"
        p = Part(name=NAME, barcode=BARCODE)
        db.session.add(p)
        i = Inventory(part=p)
        db.session.add(i)
        db.session.commit()

        self.assertEqual(Inventory.query.count(), 1)
        Inventory.archive()
        i = Inventory(part=p, quantity=2)
        db.session.add(i)
        db.session.commit()
        self.assertEqual(Inventory.query.count(), 2)
        output = Inventory._export_csv().getvalue().strip()
        self.assertEqual(len(output.split("\n")), 2)
        header, content = output.split("\n")
        self.assertEqual(
            header, "id,part_name,part_barcode,quantity,created_at,updated_at"
        )
        self.assertTrue("BARCODE,QWERTY1234,2.0," in content)


if __name__ == "__main__":
    unittest.main()

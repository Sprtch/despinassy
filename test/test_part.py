import unittest
from despinassy import db, Part, Inventory
import sqlalchemy

class TestDatabasePart(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db.init_app(config={
            'uri': 'sqlite://',
        })
        db.drop_all()
        db.create_all()

    @classmethod
    def tearDownClass(self):
        db.drop_all()

    def tearDown(self):
        Part.query.delete()

    def test_part_creation(self):
        p = Part(name="BARCODE", barcode="QWERTY1234")
        db.session.add(p)
        db.session.commit()
        self.assertEqual(Part.query.count(), 1)

    def test_part_query(self):
        x = Part(name="BARCODE", barcode="QWERTY1234")
        db.session.add(x)
        db.session.commit()
        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        self.assertEqual(p.id, 1)
        self.assertEqual(p.name, "BARCODE")
        self.assertEqual(p.barcode, "QWERTY1234")
        self.assertEqual(p.counter, 0)

    def test_part_unique(self):
        x = Part(name="BARCODE", barcode="QWERTY1234")
        db.session.add(x)
        db.session.commit()
        p = Part(name="BARCODE2", barcode="QWERTY1234")
        db.session.add(p)
        self.assertRaises(sqlalchemy.exc.IntegrityError, db.session.commit)
        db.session.rollback()

    def test_part_delete(self):
        x = Part(name="BARCODE", barcode="QWERTY1234")
        db.session.add(x)
        db.session.commit()
        self.assertNotEqual(Part.query.count(), 0)
        Part.query.delete()
        db.session.commit()
        self.assertEqual(Part.query.count(), 0)

    def test_part_long_barcode(self):
        longbarcode = "X" * 256
        self.assertRaises(sqlalchemy.exc.ArgumentError, Part, name="foo", barcode=longbarcode)


    def test_part_long_name(self):
        longname = "X" * 256
        x = Part(name=longname, barcode="foo")
        db.session.add(x)
        db.session.commit()
        self.assertEqual(len(x.name), 128) 



if __name__ == '__main__':
    unittest.main()

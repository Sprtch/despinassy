import unittest
from despinassy import db, Part, Inventory
import sqlalchemy

class TestDatabasePart(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db.init_app(config={
            'uri': 'sqlite://',
        })
        db.create_all()

    def test_part_creation(self):
        p = Part(name="BARCODE", barcode="QWERTY1234")
        db.session.add(p)
        db.session.commit()
        self.assertEqual(Part.query.count(), 1)

    def test_part_query(self):
        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        self.assertEqual(p.id, 1)
        self.assertEqual(p.name, "BARCODE")
        self.assertEqual(p.barcode, "QWERTY1234")
        self.assertEqual(p.counter, 0)

    def test_part_unique(self):
        p = Part(name="BARCODE2", barcode="QWERTY1234")
        db.session.add(p)
        self.assertRaises(sqlalchemy.exc.IntegrityError, db.session.commit)

if __name__ == '__main__':
    unittest.main()

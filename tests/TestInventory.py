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

    def test_inventory_creation(self):
        p = Part(name="BARCODE", barcode="QWERTY1234")
        db.session.add(p)
        i = Inventory(part=p)
        db.session.add(i)
        db.session.commit()
        self.assertEqual(Inventory.query.count(), 1)

    def test_inventory_query1(self):
        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        
        self.assertEqual(len(p.inventories), 1)

    def test_inventory_query2(self):
        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        i = p.inventories[0]
        self.assertEqual(i.part_id, p.id)

    def test_inventory_query3(self):
        p = Part.query.delete()
        self.assertEqual(Inventory.query.count(), 0)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
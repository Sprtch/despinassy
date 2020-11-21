import unittest
from despinassy import db, Part, Inventory
import sqlalchemy

class TestDatabaseInventory(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db.init_app(config={
            'uri': 'sqlite://',
        })
        db.create_all()

    @classmethod
    def tearDownClass(self):
        db.drop_all()

    def test_inventory_creation(self):
        p = Part(name="BARCODE", barcode="QWERTY1234")
        db.session.add(p)
        i = Inventory(part=p)
        db.session.add(i)
        db.session.commit()
        self.assertEqual(Inventory.query.count(), 1)

    def test_inventory_query_1(self):
        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        
        self.assertEqual(len(p.inventories), 1)

    def test_inventory_query_2(self):
        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        i = p.inventories[0]
        self.assertEqual(i.part_id, p.id)

    def test_inventory_query_3(self):
        Inventory.query.delete()
        self.assertEqual(Inventory.query.count(), 0)

if __name__ == '__main__':
    unittest.main()

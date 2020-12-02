import unittest
from despinassy import db, Part, Inventory
import sqlalchemy

class TestDatabaseInventory(unittest.TestCase):
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
        Inventory.query.delete()
        Part.query.delete()

    @staticmethod
    def inventory_creation(name, barcode):
        p = Part(name=name, barcode=barcode)
        db.session.add(p)
        i = Inventory(part=p)
        db.session.add(i)
        db.session.commit()

    def test_inventory_query_1(self):
        self.assertEqual(Inventory.query.count(), 0)
        TestDatabaseInventory.inventory_creation("BARCODE", "QWERTY1234")
        self.assertEqual(Inventory.query.count(), 1)
        TestDatabaseInventory.inventory_creation("BARCODE 2", "HELLO1234")
        self.assertEqual(len(Part.query.filter(Part.barcode == "HELLO1234").all()), 1)
        self.assertEqual(Inventory.query.count(), 2)

        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        self.assertEqual(len(p.inventories), 1)

    def test_inventory_query_2(self):
        self.assertEqual(Inventory.query.count(), 0)
        TestDatabaseInventory.inventory_creation("BARCODE", "QWERTY1234")
        self.assertEqual(Inventory.query.count(), 1)
        TestDatabaseInventory.inventory_creation("BARCODE 2", "HELLO1234")
        self.assertEqual(len(Part.query.filter(Part.barcode == "HELLO1234").all()), 1)
        self.assertEqual(Inventory.query.count(), 2)

        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        i = p.inventories[0]
        self.assertEqual(i.part_id, p.id)

    def test_inventory_query_3(self):
        TestDatabaseInventory.inventory_creation("BARCODE", "QWERTY1234")
        self.assertEqual(Inventory.query.count(), 1)
        TestDatabaseInventory.inventory_creation("BARCODE 2", "HELLO1234")
        self.assertEqual(len(Part.query.filter(Part.barcode == "HELLO1234").all()), 1)
        self.assertEqual(Inventory.query.count(), 2)

        p = Part.query.filter(Part.barcode == "HELLO1234").first()
        i = Inventory.retrieve_inventory_from_barcode("HELLO1234")
        self.assertEqual(i.part_id, p.id)

    def test_inventory_query_4(self):
        TestDatabaseInventory.inventory_creation("BARCODE", "QWERTY1234")
        self.assertEqual(Inventory.query.count(), 1)
        TestDatabaseInventory.inventory_creation("BARCODE 2", "HELLO1234")
        self.assertEqual(len(Part.query.filter(Part.barcode == "HELLO1234").all()), 1)
        self.assertEqual(Inventory.query.count(), 2)

        Inventory.query.delete()
        self.assertEqual(Inventory.query.count(), 0)

if __name__ == '__main__':
    unittest.main()

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

    def test_inventory_creation_1(self):
        BARCODE = "QWERTY1234"
        NAME = "BARCODE"
        p = Part(name=NAME, barcode=BARCODE)
        db.session.add(p)
        i = Inventory(part=p)
        db.session.add(i)
        db.session.commit()
        self.assertEqual(Inventory.query.count(), 1)

    def test_inventory_creation_2(self):
        BARCODE = "HELLO1234"
        NAME = "BARCODE 2"
        p = Part(name=NAME, barcode=BARCODE)
        db.session.add(p)
        i = Inventory(part=p)
        db.session.add(i)
        db.session.commit()

        self.assertEqual(len(Part.query.filter(Part.barcode == BARCODE).all()), 1)

        # Inventory.create_inventory_from_barcode("HELLO1234")

        self.assertEqual(Inventory.query.count(), 2)

    def test_inventory_query_1(self):
        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        
        self.assertEqual(len(p.inventories), 1)

    def test_inventory_query_2(self):
        p = Part.query.filter(Part.barcode == "QWERTY1234").first()
        i = p.inventories[0]
        self.assertEqual(i.part_id, p.id)

    def test_inventory_query_3(self):
        p = Part.query.filter(Part.barcode == "HELLO1234").first()

        i = Inventory.retrieve_inventory_from_barcode("HELLO1234")

        self.assertEqual(i.part_id, p.id)

    def test_inventory_query_4(self):
        Inventory.query.delete()
        self.assertEqual(Inventory.query.count(), 0)

if __name__ == '__main__':
    unittest.main()

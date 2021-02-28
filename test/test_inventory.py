import unittest
from despinassy import db, Part, Inventory
from despinassy.Inventory import InventorySession


class TestDatabaseInventory(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db.init_app(
            config={
                "uri": "sqlite://",
            }
        )
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
        return i

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

    def test_inventory_delete(self):
        TestDatabaseInventory.inventory_creation("BARCODE", "QWERTY1234")
        self.assertEqual(Inventory.query.count(), 1)
        TestDatabaseInventory.inventory_creation("BARCODE 2", "HELLO1234")
        self.assertEqual(len(Part.query.filter(Part.barcode == "HELLO1234").all()), 1)
        self.assertEqual(Inventory.query.count(), 2)

        Inventory.query.delete()
        self.assertEqual(Inventory.query.count(), 0)

    def test_inventory_quantity(self):
        i1 = TestDatabaseInventory.inventory_creation("BARCODE", "QWERTY1234")
        self.assertEqual(Inventory.query.count(), 1)
        i2 = TestDatabaseInventory.inventory_creation("BARCODE 2", "HELLO1234")
        self.assertEqual(len(Part.query.filter(Part.barcode == "HELLO1234").all()), 1)
        self.assertEqual(Inventory.query.count(), 2)

        self.assertEqual(i1.quantity, 0)
        self.assertEqual(i2.quantity, 0)

        i1.add()
        self.assertEqual(i1.quantity, 1)
        i2.add(3)
        self.assertEqual(i2.quantity, 3)
        i1.add(2)
        self.assertEqual(i1.quantity, 3)

    def test_inventory_session(self):
        i1 = TestDatabaseInventory.inventory_creation("BARCODE", "QWERTY1234")
        self.assertEqual(Inventory.query.count(), 1)
        is1 = InventorySession.query.get(0)
        self.assertEqual(i1.session, is1)

    def test_inventory_to_dict(self):
        result = {
            "id": 1,
            "part": {
                "id": 1,
                "barcode": "QWERTY1234",
                "name": "BARCODE",
                "counter": 0,
            },
            "quantity": 0,
        }
        i1 = TestDatabaseInventory.inventory_creation("BARCODE", "QWERTY1234")
        self.assertEqual(Inventory.query.count(), 1)

        self.assertEqual(i1.to_dict(), result)


if __name__ == "__main__":
    unittest.main()

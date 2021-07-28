import unittest
import json
from despinassy import db
from despinassy.ipc import IpcPrintMessage, IpcOrigin
from despinassy.Printer import (
    Printer,
    PrinterTransaction,
    PrinterDialectEnum,
    PrinterTypeEnum,
)
from despinassy.Channel import Channel


class TestDatabasePrinter(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        db.init_app(
            config={
                "uri": "sqlite://",
            }
        )
        db.drop_all()

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def test_printer_creation(self):
        p = Printer(
            name="main",
            type=1,
            dialect=1,
            redis="victoria",
            settings='{"address": "192.168.0.1"}',
        )
        db.session.add(p)
        db.session.commit()
        self.assertEqual(Printer.query.count(), 1)
        self.assertEqual(p.type, PrinterTypeEnum.STDOUT)
        self.assertEqual(p.dialect, PrinterDialectEnum.ZEBRA_ZPL)
        self.assertEqual(Printer.query.get(p.id), p)
        self.assertEqual(json.loads(p.settings)["address"], "192.168.0.1")

    def test_printer_transaction(self):
        p = Printer(
            name="main",
            type=1,
            dialect=1,
            redis="victoria",
            settings='{"address": "192.168.0.1"}',
        )
        db.session.add(p)
        pt = PrinterTransaction(
            printer=p, name="bar", barcode="FOO", origin=IpcOrigin.TEST
        )
        db.session.add(pt)
        db.session.commit()
        self.assertEqual(Printer.query.count(), 1)
        self.assertEqual(PrinterTransaction.query.count(), 1)
        self.assertEqual(len(p.transactions), 1)
        self.assertEqual(p.transactions[0], pt)

    def test_printer_add_transaction(self):
        msg = IpcPrintMessage(
            barcode="hello",
            name="world",
            origin=IpcOrigin.TEST,
            destination="victoria",
            number=1,
        )
        p = Printer(
            name="main",
            type=1,
            dialect=1,
            redis="victoria",
            settings='{"address": "192.168.0.1"}',
        )
        db.session.add(p)
        pt = p.add_transaction(**msg._asdict())
        db.session.add(pt)
        db.session.commit()
        self.assertEqual(Printer.query.count(), 1)
        self.assertEqual(PrinterTransaction.query.count(), 1)
        self.assertEqual(len(p.transactions), 1)
        self.assertEqual(p.transactions[0], pt)

    def test_printer_transaction_order(self):
        """
        Verify the order of the 'Printer' table 'transactions' field.
        The last added transactions should be the first one in the
        transaction list.
        """
        p = Printer(
            name="main",
            type=1,
            dialect=1,
            redis="victoria",
            settings='{"address": "192.168.0.1"}',
        )
        db.session.add(p)
        pt1 = p.add_transaction(origin=IpcOrigin.TEST, barcode="foo", name="bar")
        db.session.add(pt1)
        pt2 = p.add_transaction(origin=IpcOrigin.TEST, barcode="hello", name="world")
        db.session.add(pt2)
        db.session.commit()
        self.assertEqual(len(p.transactions), 2)
        self.assertEqual(p.transactions[0].name, "world")
        self.assertEqual(p.transactions[1].name, "bar")


if __name__ == "__main__":
    unittest.main()

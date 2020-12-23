import unittest
import json
from despinassy import db
from despinassy.Printer import Printer, PrinterDialectEnum, PrinterTypeEnum


class TestDatabasePrinter(unittest.TestCase):
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
        Printer.query.delete()

    def test_printer_creation(self):
        p = Printer(name="main",
                    type=1,
                    dialect=1,
                    redis="victoria",
                    settings='{"address": "192.168.0.1"}')
        db.session.add(p)
        db.session.commit()
        self.assertEqual(Printer.query.count(), 1)
        self.assertEqual(p.type, PrinterTypeEnum.STDOUT)
        self.assertEqual(p.dialect, PrinterDialectEnum.ZEBRA_ZPL)
        self.assertEqual(Printer.query.get(p.id), p)
        self.assertEqual(json.loads(p.settings)['address'], "192.168.0.1")


if __name__ == '__main__':
    unittest.main()

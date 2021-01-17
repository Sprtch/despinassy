import unittest
from despinassy import db
from despinassy.Printer import Printer, PrinterDialectEnum, PrinterTypeEnum
from despinassy.Scanner import Scanner, ScannerTypeEnum, ScannerModeEnum
from despinassy.Channel import Channel


class TestDatabaseChannel(unittest.TestCase):
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
        Scanner.query.delete()
        Channel.query.delete()

    def test_same_channel(self):
        p1 = Printer(name="main",
                     type=1,
                     dialect=1,
                     redis="victoria",
                     settings='{"address": "192.168.0.1"}')
        db.session.add(p1)
        p2 = Printer(name="second",
                     type=1,
                     dialect=1,
                     redis="victoria",
                     settings='{"address": "192.168.0.1"}')
        db.session.add(p2)

        s = Scanner(name="main",
                    type=ScannerTypeEnum.TEST,
                    redis="victoria",
                    settings='{}')
        db.session.add(s)

        self.assertEqual(Channel.query.count(), 1)
        self.assertEqual(Scanner.query.count(), 1)
        self.assertEqual(Printer.query.count(), 2)


if __name__ == '__main__':
    unittest.main()

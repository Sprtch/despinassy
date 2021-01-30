import unittest
from despinassy import db
from despinassy.Scanner import Scanner, ScannerTransaction, ScannerTypeEnum, ScannerModeEnum
from despinassy.Channel import Channel


class TestDatabaseScanner(unittest.TestCase):
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

    def setUp(self):
        c = Channel(name="victoria")
        db.session.add(c)
        db.session.commit()

    def tearDown(self):
        Channel.query.delete()
        Scanner.query.delete()
        ScannerTransaction.query.delete()

    def test_scanner_creation(self):
        s = Scanner(name="main",
                    type=ScannerTypeEnum.TEST,
                    redis="victoria",
                    settings='{}')
        db.session.add(s)
        db.session.commit()
        self.assertEqual(Scanner.query.count(), 1)
        self.assertEqual(s.type, ScannerTypeEnum.TEST)
        self.assertEqual(Scanner.query.get(s.id), s)

    def test_scanner_transaction(self):
        s = Scanner(name="main",
                    type=ScannerTypeEnum.TEST,
                    redis="victoria",
                    settings='{}')
        db.session.add(s)
        st = ScannerTransaction(scanner=s,
                                mode=ScannerModeEnum.PRINTMODE,
                                value="FOOBAR123")
        db.session.add(st)
        db.session.commit()
        self.assertEqual(Scanner.query.count(), 1)
        self.assertEqual(ScannerTransaction.query.count(), 1)
        self.assertEqual(len(s.transactions), 1)
        self.assertEqual(s.transactions[0], st)

    def test_scanner_add_transaction(self):
        s = Scanner(name="main",
                    type=ScannerTypeEnum.TEST,
                    redis="victoria",
                    settings='{}')
        db.session.add(s)
        st = s.add_transaction(mode=ScannerModeEnum.PRINTMODE,
                               value="FOOBAR123")
        db.session.add(st)
        db.session.commit()
        self.assertEqual(Scanner.query.count(), 1)
        self.assertEqual(ScannerTransaction.query.count(), 1)
        self.assertEqual(len(s.transactions), 1)
        self.assertEqual(s.transactions[0], st)

    def test_scanner_transaction_order(self):
        """
        Verify the order of the 'Scanner' table 'transactions' field.
        The last added transactions should be the first one in the 
        transaction list.
        """
        s = Scanner(name="main",
                    type=ScannerTypeEnum.TEST,
                    redis="victoria",
                    settings='{}')
        db.session.add(s)
        st1 = s.add_transaction(mode=ScannerModeEnum.PRINTMODE,
                               value="FOOBAR123")
        db.session.add(st1)
        st2 = s.add_transaction(mode=ScannerModeEnum.PRINTMODE,
                               value="HELLOWORLD")
        db.session.add(st2)
        db.session.commit()

        self.assertEqual(len(s.transactions), 2)
        self.assertEqual(s.transactions[0].value, "HELLOWORLD")
        self.assertEqual(s.transactions[1].value, "FOOBAR123")


if __name__ == '__main__':
    unittest.main()

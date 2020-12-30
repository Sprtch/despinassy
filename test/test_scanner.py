import unittest
import json
from despinassy import db
from despinassy.Scanner import Scanner, ScannerTypeEnum


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

    def tearDown(self):
        Scanner.query.delete()

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


if __name__ == '__main__':
    unittest.main()

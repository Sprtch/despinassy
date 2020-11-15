import unittest
from despinassy.ipc import IpcPrintMessage, ipc_create_print_message, redis_subscribers_num
from collections import namedtuple

class TestRedis(unittest.TestCase):
    def test_msg_cast1(self):
        TestMessage = namedtuple('PrintMessage', 'barcode, origin, redis, name')
        msg = TestMessage(barcode="1234", origin="here", redis="redis", name="1234")
        a = ipc_create_print_message(msg)

        self.assertTrue(isinstance(a, IpcPrintMessage))
        self.assertEqual(a.barcode, "1234")
        self.assertEqual(a.origin, "here")
        self.assertEqual(a.name, "1234")
        self.assertEqual(a.number, 1)

    def test_msg_cast2(self):
        TestMessage = namedtuple('PrintMessage', 'barcode, origin, redis, name')
        msg = TestMessage(barcode="1234", origin="here", redis="redis", name="1234")
        a = ipc_create_print_message(msg, name="New Name")

        self.assertTrue(isinstance(a, IpcPrintMessage))
        self.assertEqual(a.barcode, "1234")
        self.assertEqual(a.origin, "here")
        self.assertEqual(a.name, "New Name")
        self.assertEqual(a.number, 1)

    def test_msg_cast3(self):
        TestMessage = namedtuple('PrintMessage', 'barcode, origin, redis, name')
        msg = dict(barcode="1234", origin="here", redis="redis", name="1234")
        a = ipc_create_print_message(msg)

        self.assertTrue(isinstance(a, IpcPrintMessage))
        self.assertEqual(a.barcode, "1234")
        self.assertEqual(a.origin, "here")
        self.assertEqual(a.name, "1234")
        self.assertEqual(a.number, 1)

    def test_msg_cast4(self):
        msg = IpcPrintMessage(barcode="hello")

        self.assertTrue(isinstance(msg, IpcPrintMessage))
        self.assertEqual(msg.barcode, "hello")
        self.assertEqual(msg.origin, None)
        self.assertEqual(msg.name, '')
        self.assertEqual(msg.number, 1)

if __name__ == '__main__':
    unittest.main()

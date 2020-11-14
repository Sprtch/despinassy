import unittest
from despinassy.ipc import IpcPrintMessage, ipc_create_print_message, redis_subscribers_num
from collections import namedtuple

class TestRedis(unittest.TestCase):
    def test_msg_cast(self):
        TestMessage = namedtuple('PrintMessage', 'barcode, origin, redis, name')
        msg = TestMessage(barcode="1234", origin="here", redis="redis", name="1234")
        a = ipc_create_print_message(msg)

        self.assertTrue(isinstance(a, IpcPrintMessage))

if __name__ == '__main__':
    unittest.main()

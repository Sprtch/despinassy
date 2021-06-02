import unittest
from despinassy.ipc import (
    IpcMessageType,
    IpcOrigin,
    IpcPrintMessage,
    ipc_create_print_message,
    redis_subscribers_num,
)
from collections import namedtuple
import dataclasses
import json


class TestRedis(unittest.TestCase):
    def test_msg_cast1(self):
        TestMessage = namedtuple("PrintMessage", "barcode, origin, redis, name")
        msg = TestMessage(
            barcode="1234", origin=IpcOrigin.TEST, redis="redis", name="1234"
        )
        a = ipc_create_print_message(msg)

        self.assertTrue(isinstance(a, IpcPrintMessage))
        self.assertEqual(a.barcode, "1234")
        self.assertEqual(a.origin, IpcOrigin.TEST)
        self.assertEqual(a.name, "1234")
        self.assertEqual(a.number, 1)

    def test_msg_cast2(self):
        TestMessage = namedtuple("PrintMessage", "barcode, origin, redis, name")
        msg = TestMessage(
            barcode="1234", origin=IpcOrigin.TEST, redis="redis", name="1234"
        )
        a = ipc_create_print_message(msg, name="New Name")

        self.assertTrue(isinstance(a, IpcPrintMessage))
        self.assertEqual(a.barcode, "1234")
        self.assertEqual(a.origin, IpcOrigin.TEST)
        self.assertEqual(a.name, "New Name")
        self.assertEqual(a.number, 1)

    def test_msg_cast3(self):
        TestMessage = namedtuple("PrintMessage", "barcode, origin, redis, name")
        msg = dict(barcode="1234", origin=IpcOrigin.TEST, redis="redis", name="1234")
        a = ipc_create_print_message(msg)

        self.assertTrue(isinstance(a, IpcPrintMessage))
        self.assertEqual(a.barcode, "1234")
        self.assertEqual(a.origin, IpcOrigin.TEST)
        self.assertEqual(a.name, "1234")
        self.assertEqual(a.number, 1)

    def test_msg_cast4(self):
        msg = IpcPrintMessage(barcode="hello")

        self.assertTrue(isinstance(msg, IpcPrintMessage))
        self.assertEqual(msg.barcode, "hello")
        self.assertEqual(msg.origin, IpcOrigin.UNDEFINED)
        self.assertEqual(msg.name, "")
        self.assertEqual(msg.number, 1)

    def test_msg_dict1(self):
        msgdict = dict(
            barcode="barcode",
            name="name",
            origin=IpcOrigin.TEST,
            destination="",
            msg_type=IpcMessageType.PRINT,
            number=1,
            device=None,
        )
        msg = ipc_create_print_message({}, **msgdict)
        self.assertEqual(msgdict, msg._asdict())

    def test_msg_serialize1(self):
        i = IpcPrintMessage(
            barcode="barcode",
            name="name",
            origin=IpcOrigin.TEST,
            number=1,
            device=None,
        )
        dump = json.dumps(i._asdict())
        self.assertEqual(
            dump,
            '{"destination": "", "origin": 1, "device": null, "msg_type": 1, "barcode": "barcode", "name": "name", "number": 1}',
        )
        ii = IpcPrintMessage(**json.loads(dump))
        self.assertEqual(ii, i)


if __name__ == "__main__":
    unittest.main()

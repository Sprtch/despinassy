import unittest
from despinassy.ipc import (
    IpcOrigin,
    IpcPrintMessage,
)
import json


class TestIpc(unittest.TestCase):
    def test_msg_asdict(self):
        i = IpcPrintMessage(
            barcode="barcode",
            name="name",
            origin=IpcOrigin.TEST,
            destination="victoria",
            number=1,
            device=None,
        )
        d = i._asdict()
        print(d)
        self.assertEqual(d["barcode"], "barcode")
        self.assertEqual(d["name"], "name")
        self.assertEqual(d["origin"], 1)
        self.assertEqual(d["destination"], "victoria")
        self.assertEqual(d["number"], 1)
        self.assertEqual(d["msg_type"], 1)
        self.assertEqual(d["device"], None)

    def test_msg_serialize1(self):
        i = IpcPrintMessage(
            barcode="barcode",
            name="name",
            origin=IpcOrigin.TEST,
            destination="victoria",
            number=1,
            device=None,
        )
        dump = json.dumps(i._asdict())
        self.assertEqual(
            dump,
            '{"destination": "victoria", "origin": 1, "device": null, "msg_type": 1, "barcode": "barcode", "name": "name", "number": 1}',
        )
        ii = IpcPrintMessage(**json.loads(dump))
        self.assertEqual(ii, i)


if __name__ == "__main__":
    unittest.main()

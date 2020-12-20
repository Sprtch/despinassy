import dataclasses
from enum import IntEnum
from typing import Optional, Union
import json


class IpcOrigin(IntEnum):
    UNDEFINED = 0
    TEST = 1
    HURON = 2
    ERIE = 3


@dataclasses.dataclass
class IpcPrintMessage:
    barcode: str = ""
    origin: IpcOrigin = IpcOrigin.UNDEFINED
    device: Optional[str] = None
    name: str = ""
    number: Union[int, float] = 1.0

    def __post_init__(self):
        self.barcode = str(self.barcode)
        self.origin = IpcOrigin(self.origin)
        self.name = str(self.name)
        self.number = float(self.number)

    def _asdict(self):
        return dataclasses.asdict(self)


def create_nametuple(target, instance, **kwargs):
    msg_dict = {}
    fields = []
    if hasattr(target, '_fields'):
        fields = target._fields
    else:
        fields = list(map(lambda x: x.name, dataclasses.fields(target)))

    if isinstance(instance, dict):
        for f in fields:
            if f in instance:
                msg_dict[f] = kwargs.get(f) or instance[f]
            elif f in kwargs:
                msg_dict[f] = kwargs.get(f)
    else:
        for f in fields:
            if hasattr(instance, f):
                msg_dict[f] = kwargs.get(f) or getattr(instance, f)
            elif f in kwargs:
                msg_dict[f] = kwargs.get(f)

    return target(**msg_dict)


def ipc_create_print_message(instance, **kwargs):
    return create_nametuple(IpcPrintMessage, instance, **kwargs)


def redis_subscribers_num(redis, channel):
    return redis.execute_command('PUBSUB', 'NUMSUB', channel)[1]


def redis_send_to_print(redis, channel, msg: IpcPrintMessage, **kwargs):
    if redis_subscribers_num(redis, channel):
        return redis.publish(channel, json.dumps(msg._asdict()))
    else:
        return None

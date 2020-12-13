import dataclasses
from enum import IntEnum
from typing import Optional

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
    number: int = 1

    def __post_init__(self):
        self.origin = IpcOrigin(self.origin) # TODO how to automatically create IpcOrigin object from int at creation ?
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if hasattr(field.type, "__args__") and len(field.type.__args__) == 2 and field.type.__args__[-1] is type(None):
                if value is not None and not isinstance(value, field.type.__args__[0]):
                    raise ValueError(f'Expected {field.name} to be either {field.type.__args__[0]} or None')
            elif not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                f'got {repr(value)}')

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
    if redis_subscribers_num(r, channel):
       return r.publish(
           chan,
           json.dumps(msg._asdict())
       )
    else:
       return None

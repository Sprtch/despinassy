from collections import namedtuple

IpcPrintMessage = namedtuple('PrintMessage', 'barcode, origin, name')

def create_nametuple(target, instance, **kwargs):
    msg_dict = {}
    if isinstance(instance, dict):
        for f in target._fields:
            if instance.get(f) is not None:
                msg_dict[f] = kwargs.get(f) or instance[f]
            else:
                msg_dict[f] = kwargs.get(f)
    else:
        for f in target._fields:
            if hasattr(instance, f):
                msg_dict[f] = kwargs.get(f) or getattr(instance, f)
            else:
                msg_dict[f] = kwargs.get(f)

    return target(**msg_dict)

def ipc_create_print_message(instance, **kwargs):
    return create_nametuple(IpcPrintMessage, instance, **kwargs)

def redis_subscribers_num(redis, channel):
    return redis.execute_command('PUBSUB', 'NUMSUB', channel)[1]

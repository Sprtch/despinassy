from collections import namedtuple

IpcPrintMessage = namedtuple('PrintMessage', 'barcode, origin, name')

def ipc_create_print_message(instance):
    msg_dict = {}
    for f in IpcPrintMessage._fields:
        if hasattr(instance, f):
            msg_dict[f] = getattr(instance, f)
        else:
            msg_dict[f] = None

    return IpcPrintMessage(**msg_dict)

def redis_subscribers_num(redis, channel):
    return redis.execute_command('PUBSUB', 'NUMSUB', channel)[1]

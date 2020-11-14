from collections import namedtuple

BarcodeMessage = namedtuple('BarcodeMessage', 'barcode, origin, redis')
RedisPrintMessage = namedtuple('BarcodeMessage', 'barcode, origin, redis, name')

def redis_subscribers_num(redis, channel):
    return redis.execute_command('PUBSUB', 'NUMSUB', channel)[1]

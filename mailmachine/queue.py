import hotqueue
import simplejson

class HotQueue(hotqueue.HotQueue):

    def snapshot(self):
        # list content without consuming queue
        return [self.serializer.loads(c) for c in self._HotQueue__redis.lrange(self.key, 0, len(self)-1)]


class MailQueue(object):

    def __init__(self, name, **kwargs):
        self.name = name
        kwargs.setdefault('serializer', simplejson)
        self._queue = HotQueue(name, **kwargs)

    def put(self, from_email, recipients, msg):
        self._queue.put((from_email, recipients, msg))

    def get(self, block=False, timeout=None):
        return self._queue.get(block, timeout)

    def snapshot(self):
        # list content without consuming queue
        return self._queue.snapshot()

    def worker(self, *args, **kwargs):
        return self._queue.worker(*args, **kwargs)

import hotqueue
import simplejson

class MailQueue(object):

    def __init__(self, name, **kwargs):
        self.name = name
        kwargs.setdefault('serializer', simplejson)
        self._queue = hotqueue.HotQueue(name, **kwargs)

    def put(self, from_email, recipients, msg):
        self._queue.put((from_email, recipients, msg))

    def get(self, block=False, timeout=None):
        return self._queue.get(block, timeout)

    def snapshot(self):
        # list content without consuming queue
        mails = []
        q = self._queue
        for mail in [q.serializer.loads(c) for c in q._HotQueue__redis.lrange(q.key, 0, len(q)-1)]:
            mails.append(mail)
        return mails

    def worker(self, *args, **kwargs):
        return self._queue.worker(*args, **kwargs)

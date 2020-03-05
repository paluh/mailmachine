import base64
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

    def put(self, subject, body, from_email, recipients,
            alternatives=None, attachments=None, sent=None):

        attachments = map(lambda a: ({'file_name': a[0], 'content': base64.b64encode(a[1]), 'mime': a[2]}),
                          attachments or [])
        alternatives = map(lambda a: (base64.b64encode(a[0]), a[1]), alternatives or [])

        self._queue.put({'subject': subject, 'body': body, 'from_email': from_email,
                         'recipients': recipients, 'alternatives': alternatives,
                         'attachments': attachments})

    def get(self, block=False, timeout=None):
        message = self._queue.get(block, timeout)

        message['alternatives'] = map(lambda a: (base64.b64decode(a[0]), a[1]), message['alternatives'])

        message['attachments'] = map(lambda a: (a['file_name'],
                                     base64.b64decode(a['content']), a['mime']), message['attachments'])
        return message

    def snapshot(self):
        # list content without consuming queue
        return self._queue.snapshot()

    def worker(self, fun, timeout=None):
        while True:
            fun(self.get(block=True, timeout=timeout))

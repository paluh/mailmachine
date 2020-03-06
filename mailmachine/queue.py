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

        # In general we want(!?) (I'm not sure about that)
        # just accept base64 encoded
        # anything and decode it to unicode if it is a text
        # according to a given charset.
        #
        # TODO: Check character set here!
        #
        # Don't ask me why we ended up here
        # but I'm treating `text/*` mime as utf-8
        # strings so they are send as nice plain text
        # alternative...
        #
        def decode_alternative(a):
            payload = a[0]
            mime = a[1]
            if mime.split('/')[0] == 'text':
                try:
                    buf = base64.b64decode(payload)
                    try:
                        # base64 encoded utf-8 text
                        return(buf.decode('utf-8'), mime)
                    except:
                        # base64 encoded some text
                        # we are returning buf
                        # because email_message is able
                        # to cope with that...
                        return (buf, mime)
                except:
                    # XXX: Backward compatibility
                    # non base64 encoded string
                    if isinstance(payload, unicode):
                        return (payload, mime)

            else:
                # In case of anything else we should just pass buffer
                # to the email_message. It can handle this by..
                # encoding it back to base64 :-P
                return (base64.b64decode(a[0]), mime)

        message['alternatives'] = map(decode_alternative, message['alternatives'])

        message['attachments'] = map(lambda a: (a['file_name'],
                                     base64.b64decode(a['content']), a['mime']), message['attachments'])
        return message

    def snapshot(self):
        # list content without consuming queue
        return self._queue.snapshot()

    def worker(self, fun, timeout=None):
        while True:
            fun(self.get(block=True, timeout=timeout))

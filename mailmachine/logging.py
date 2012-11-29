from __future__ import absolute_import
import logging
import hotqueue
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonTracebackLexer


class MailMachineLoggingHandler(logging.Handler):

    def __init__(self, level, from_email, recipients, subject, mail_queue,
                 redis_host, redis_port, redis_password):
        super(MailMachineLoggingHandler, self).__init__(self, level)
        self.from_email = from_email
        self.recipients = recipients
        self.subject = subject
        self._mail_queue = hotqueue.HotQueue(mail_queue, host=redis_host, port=redis_port,
                                             password=redis_password)

    def emit(self, record):
        try:
            alternatives = []
            mail = {
                'alternatives': alternatives,
                'body': self.format(record),
                'subject': self.subject,
                'from_email': self.from_email,
                'recipients': self.recipients,
            }

            if record.exc_text:
                html_formatter = HtmlFormatter(noclasses=True)
                tb = highlight(record.exc_text, PythonTracebackLexer(), html_formatter)

                info = (self.formatter or logging._defaultFormatter)._fmt % record.__dict__
                info = '<p style="white-space: pre-wrap; word-wrap: break-word;">%s</p>' % info

                html = ('<html><head></head><body>%s<div style="font-size:120%%">%s</div></body></html>')% (info, tb)
                alternatives.append((html, 'html'))
            self.mail_queue.put(mail)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


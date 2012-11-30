from __future__ import absolute_import
import calendar
import datetime
from email_message import get_connection
import logging
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonTracebackLexer

from .mail import enqueue, send


class MailMachineLoggingHandlerBase(logging.Handler):

    def __init__(self, from_email, recipients, subject, *args, **kwargs):
        super(MailMachineLoggingHandlerBase, self).__init__(*args, **kwargs)
        self.from_email = from_email
        self.recipients = recipients
        self.subject = subject

    def emit(self, record):
        try:
            alternatives = []
            if record.exc_text:
                html_formatter = HtmlFormatter(noclasses=True)
                tb = highlight(record.exc_text, PythonTracebackLexer(), html_formatter)

                info = (self.formatter or logging._defaultFormatter)._fmt % record.__dict__
                info = '<p style="white-space: pre-wrap; word-wrap: break-word;">%s</p>' % info

                html = ('<html><head></head><body>%s<div style="font-size:120%%">%s</div></body></html>')% (info, tb)
                alternatives.append({'content': html, 'mime': 'text/html'})
            sent = int(calendar.timegm(datetime.datetime.now().utctimetuple()))
            self.send_message(subject=self.subject, body=self.format(record), from_email=self.from_email,
                              recipients=self.recipients, alternatives=alternatives, sent=sent)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def send_message(self, **mail_data):
        raise NotImplementedError()


class EnqueueMailLoggingHandler(MailMachineLoggingHandlerBase):

    def __init__(self, mail_queue, *args, **kwargs):
        self.mail_queue = mail_queue
        super(EnqueueMailLoggingHandler, self).__init__(*args, **kwargs)

    def send_message(self, **mail_data):
        enqueue(self.mail_queue, **mail_data)


class ImmediateMailLoggingHandler(MailMachineLoggingHandlerBase):

    def __init__(self, host, port, username, password, use_tls, *args, **kwargs):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        super(ImmediateMailLoggingHandler, self).__init__(*args, **kwargs)

    def send_message(self, **mail_data):
        connection = get_connection(self.host, self.port, username=self.username,
                                    password=self.password, use_tls=self.use_tls)
        send(connection, **mail_data)


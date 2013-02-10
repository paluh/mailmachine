from __future__ import absolute_import
from email_message import get_connection
import great_justice.logging
import logging

from .mail import enqueue, send


class MailMachineLoggingHandlerBase(logging.Handler):

    def __init__(self, from_email, recipients, subject, *args, **kwargs):
        formatter = kwargs.get('formatter', great_justice.logging.Formatter())
        self.html_formatter = kwargs.pop('html_formatter', great_justice.logging.HtmlFormatter())
        super(MailMachineLoggingHandlerBase, self).__init__(*args, **kwargs)
        self.from_email = from_email
        self.recipients = recipients
        self.subject = subject
        self.formatter = formatter

    def emit(self, record):
        try:
            alternatives = []
            if record.exc_info and self.html_formatter:
                html =  self.html_formatter.format(record)
                html = '<html><head></head><body>%s</body></html>' % html
                alternatives = [(html, 'text/html')]
            self.send_message(subject=self.subject, body=self.format(record), from_email=self.from_email,
                              recipients=self.recipients, alternatives=alternatives)
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


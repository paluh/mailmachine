from __future__ import absolute_import
import calendar
import datetime
from email.utils import formatdate
import email_message

from .forms import collect_errors, EmailMessageForm

def enqueue(mail_queue, subject, body, from_email, recipients, alternatives=()):
    mail_data = {
        'subject': subject,
        'body': body,
        'from_email': from_email,
        'recipients': recipients,
        'alternatives': alternatives,
    }
    form = EmailMessageForm(mail_data)
    if not form.validate():
        errors = collect_errors(form)
        msg = 'Validation error - wrong email message format:\n%s\nerrors:\n%s\n' % (mail_data, '\n'.join('%s: %s' % (f,e) for f,e in errors))
        raise ValueError(msg)
    mail_queue.put(mail_data)

def send(connection, subject, body, from_email, recipients, alternatives):
    send_message({
        'subject': subject,
        'body': body,
        'from_email': from_email,
        'recipients': recipients,
        'alternatives': alternatives,
    }, connection=connection)

def send_message(mail, connection, logger=None):
    """Send mail which should be in following format:
        >>> mail = {
        ... 'subject': 'SPAM',
        ... 'body': 'spam spam spam',
        ... 'from_email': 'spammer@example.com',
        ... 'recipients': ['recipient1@example.com', 'recipient@example.com'],
        ... 'sent': int(calendar.timegm(datetime.datetime.now().utctimetuple())),
        ... 'alternatives': [{
        ...     'content': '<html><body><ul><li>spam</li><li>spam</li></ul></body></html>',
        ...     'mime': 'text/html'
        ... }])}
        >>> send(mail, connection, logger)
    """
    form = EmailMessageForm(mail)
    if form.validate():
        message_data = form.value.copy()
        headers = {
            'Date': formatdate(message_data.pop('sent',
                                                int(calendar.timegm(datetime.datetime.now().utctimetuple()))))
        }
        for recipient in message_data.pop('recipients'):
            alternatives = [(a['content'], a['mime']) for a in message_data.pop('alternatives')]
            message = email_message.EmailMultiAlternatives(to=[recipient], alternatives=alternatives,
                                                           headers=headers, **message_data)
            try:
                email_message.send_message(message, connection)
            except Exception, e:
                if logger:
                    logger.exception(e)
                else:
                    raise
    elif logger:
        errors = collect_errors(form)
        msg = 'Validation error - wrong email message format:\n%s\nerrors:\n%s\n' % (mail, '\n'.join('%s: %s' % (f,e) for f,e in errors))
        logger.error(msg)



from __future__ import absolute_import
import calendar
import datetime
from email.utils import formatdate
from email_message import EmailMultiAlternatives, send_message

from .forms import collect_errors, EmailMessageForm


def send(mail, connection, logger=None):
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
        message_data = form.value
        headers = {
            'Date': formatdate(form.value.pop('sent',
                                              int(calendar.timegm(datetime.datetime.now().utctimetuple()))))
        }
        for recipient in message_data.pop('recipients'):
            alternatives = [(a['content'], a['mime']) for a in message_data.pop('alternatives')]
            message = EmailMultiAlternatives(to=[recipient], alternatives=alternatives, headers=headers, **message_data)
            try:
                send_message(message, connection)
            except Exception, e:
                if logger:
                    logger.exception(e)
                else:
                    raise
    elif logger:
        errors = collect_errors(form)
        msg = 'Validation error - wrong email message format:\n%s\nerrors:\n%s\n' % (mail, '\n'.join('%s: %s' % (f,e) for f,e in errors))
        logger.error(msg)



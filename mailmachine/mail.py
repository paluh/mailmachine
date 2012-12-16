from __future__ import absolute_import
import calendar
import datetime
from email.utils import formatdate
import email_message

def enqueue(mail_queue, subject, body, from_email, recipients, alternatives=None,
            attachments=None, sent=None):
    messages = _build_messages(subject, body, from_email, recipients, alternatives, attachments, sent)
    for from_email, recipients, msg in messages:
        mail_queue.put(from_email, recipients, msg)

def send(connection, subject, body, from_email, recipients, alternatives=None,
         attachments=None, sent=None):

    messages = _build_messages(subject, body, from_email, recipients, alternatives, attachments, sent)

    for from_email, recipients, msg in messages:
        connection.sendmail(from_email, recipients, msg)

def _build_messages(subject, body, from_email, recipients, alternatives=None, attachments=None, sent=None):
    headers = {
        'Date': formatdate(sent or int(calendar.timegm(datetime.datetime.now().utctimetuple())))
    }
    messages = []
    for recipient in recipients:
        message = email_message.EmailMultiAlternatives(to=[recipient], alternatives=alternatives,
                                                       headers=headers, subject=subject, body=body,
                                                       from_email=from_email)
        for attachment in attachments:
            message.attach(*attachment)
        from_email = email_message.sanitize_address(message.from_email, message.encoding)
        recipients = [email_message.sanitize_address(addr, message.encoding) for addr in message.recipients()]
        messages.append((from_email, recipients,
                         message.message().as_string()))
    return messages


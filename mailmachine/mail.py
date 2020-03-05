from __future__ import absolute_import
from email.utils import formatdate
import  email_message
import time

def enqueue(mail_queue, subject, body, from_email, recipients, alternatives=None,
            attachments=None):
    mail_queue.put(subject=subject, body=body, from_email=from_email,
                   recipients=recipients, alternatives=alternatives,
                   attachments=attachments)

def send(connection, subject, body, from_email, recipients, alternatives=None, attachments=None):
    messages = _build_messages(subject, body, from_email, recipients, alternatives, attachments)
    for from_email, recipients, msg in messages:
        connection.sendmail(from_email, recipients, msg.encode('utf-8') if isinstance(msg, unicode) else msg)

def _build_messages(subject, body, from_email, recipients, alternatives=None, attachments=None):
    headers = {
        'Date': formatdate(int(time.time()))
    }
    messages = []
    attachments = attachments or []
    for recipient in recipients:
        message = email_message.EmailMultiAlternatives(to=[recipient], alternatives=alternatives,
                                                       headers=headers, subject=subject, body=body,
                                                       from_email=from_email, encoding='utf-8')
        for attachment in attachments:
            message.attach(*attachment)
        fe = email_message.sanitize_address(message.from_email, message.encoding)
        recipients = [email_message.sanitize_address(addr, message.encoding) for addr in message.recipients()]
        messages.append((fe, recipients,
                         message.message().as_string()))
    return messages


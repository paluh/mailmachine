from .logging import MailMachineLoggingHandler
from .forms import collect_errors, EmailMessageForm
from .mail import send_message


__all__ = ['enqueue', 'MailMachineLoggingHandler', 'send']


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

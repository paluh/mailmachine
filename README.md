Mailmachine
==========

This library implements simple, single threaded mailing worker based on redis queue (hotqueue, to be exact).

Protocol is language agnostic as worker expectes json serialized messages, but library provides only Python bindings. Of course worker daemon is also written in Python.

# Usage

    >>> from mailmachine import enqueue, get_connection, MailQueue, send
    >>> message = {
    ...     'subject': 'spam',
    ...     'body': 'spam spam spam',
    ...     'recipients': ['paluho@gmail.com'],
    ...     'from_email': 'spammer@example.com',
    ...     'alternatives': [('<html><body><ul><li>spam</li><li>spam</li></ul></body></html>', 'text/html')],
    ...     'attachments': [('spam.pdf', open('/home/spammer/documents/spam.pdf', 'r').read(), 'application/pdf')]
    ... }
    >>> # send immediately from current thread/process:
    ... connection = get_connection(host='spam.spam.spam.me', port=587, username='spammer',
    ...                             password='eggs-eggs-eggs', use_tls=True)
    >>> send(connection, **message)
    >>> # assumming that you have started mailmachined with default config you can enqueue message using default redis config and default queue (named 'mailmachine'):
    ... queue = MailQueue('mailmachine')
    >>> enqueue(queue, **message)


# Command line testing

You can also test mailmachine from command line - you have to pass json as argument:

    $ mailmachinectl -c example_config.yaml send '{"subject": spam", "body": "spam spam spam", "recipients": ["poor@recipient.com"], "from_email": "spammer@example.com", "attachments": [["/home/spammer/documents/spam.pdf", "application/pdf"]]}'

You can also use `enqueue`:

    $ mailmachined -c config.yaml &
    $ mailmachinectl -c config.yaml enqueue '{"subject": spam", "body": "spam spam spam", "recipients": ["poor@recipient.com"], "from_email": "spammer@example.com", "attachments": [["/home/spammer/documents/spam.pdf", "application/pdf"]]}'

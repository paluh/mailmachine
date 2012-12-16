# Mailmachine

## Usage

    >>> from mailmachine import send, enqueue, get_connection
    >>> from hotqueue import HotQueue
    >>> message = {
    ...     'subject': 'spam',
    ...     'body': 'spam spam spam',
    ...     'recipients': ['paluho@gmail.com'],
    ...     'from_email': 'spammer@example.com',
    ...     'alternatives': [{
    ...         'content': '<html><body><ul><li>spam</li><li>spam</li></ul></body></html>',
    ...         'mime': 'text/html'
    ...     }],
    ...     'attachments': [{
    ...         'file_name': 'spam.pdf',
    ...         'content': open('/home/spammer/documents/spam.pdf', 'r').read(),
    ...         'mime': 'application/pdf'
    ... }]}
    >>> # send immediately from current thread/process:
    ... connection = get_connection(host='spam.spam.spam.me', port=587, username='spammer',
    ...                             password='egs-egs-egs', use_tls=True)
    >>> send(connection, **message)
    >>> # assumming that you have started mailmachined with default config you can enqueue message:
    ... queue = HotQueue('mailmachine')
    >>> enqueue(queue, **message)


## Command line testing

You can also test mailmachine from command line - you have to pass json as argument:

    $ mailmachinectl -c example_config.yaml enqueue '{"subject": spam", "body": "spam spam spam", "recipients": ["poor@recipient.com"], "from_email": "spammer@example.com", "attachments": [["/home/spammer/documents/spam.pdf", "application/pdf"]]}'

You can also use `enqueue`:

    $ mailmachined -c config.yaml &
    $ mailmachinectl -c config.yaml enqueue '{"subject": spam", "body": "spam spam spam", "recipients": ["poor@recipient.com"], "from_email": "spammer@example.com", "attachments": [["/home/spammer/documents/spam.pdf", "application/pdf"]]}'

# Mailmachine
==========

Stupid simple, reliable (more than 10 years in production), single threaded mailing worker based on redis queue (hotqueue, to be exact).

Protocol is language agnostic as worker expectes a json serialized messages, library provides ~~only Python~~ [PureScript](https://github.com/paluh/purescript-mailmachine), [Haskell](https://github.com/paluh/mailmachine-hs) and Python bindings. Worker daemon is written in Python.

## Usage

    >>> from mailmachine import enqueue, get_connection, MailQueue, PROTOCOL, send
    >>> message = {
    ...     'subject': 'spam',
    ...     'body': 'spam spam spam',
    ...     'recipients': ['paluho@gmail.com'],
    ...     'from_email': 'spammer@example.com',
    ...     'alternatives': [('<html><body><ul><li>spam</li><li>spam</li></ul></body></html>', 'text/html')],
    ...     'attachments': [('spam.pdf', open('/home/spammer/documents/spam.pdf', 'r').read(), 'application/pdf')]
    ... }
    >>> # assumming that you have started mailmachined with default config you can enqueue message using default redis config and default queue (named 'mailmachine'):
    ... queue = MailQueue('mailmachine')
    >>> enqueue(queue, **message)
    >>> # you can also send an email just for testing purposes (if you want to test your smtp configuration)
        # without starting a daemon
    ... connection = get_connection(host='spam.spam.spam.me', port=587, username='spammer',
    ...                             password='eggs-eggs-eggs', protocol=PROTOCOL.TLS)
    >>> send(connection, **message)


## Command line testing

You can also test mailmachine from command line:

    $ mailmachinectl send -c config.yaml -s "spam" -b "spam spam spam" -r "poor@recipient.com" -f "spammer@example.com" -a "/home/spammer/documents/spam.pdf" "application/pdf"

You can also use `enqueue`:

    $ mailmachined -c config.yaml &
    $ mailmachinectl enqueue -c config.yaml -s "spam" -b "spam spam spam" -r "poor-recipient@example.com" -f "spammer@example.com" -a "/home/spammer/documents/spam.pdf" "application/pdf"

## Configuration

Please check [`example_config.yaml`](./example_config.yaml).

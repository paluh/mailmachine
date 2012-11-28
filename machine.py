#!/usr/bin/env python
import argparse
from email_message import EmailMultiAlternatives, get_connection, send_message
from flatland.schema import Boolean, Dict, Enum, Form, Integer, List, String
from flatland.validation.containers import HasAtLeast
from flatland.validation.scalars import Present
from flatland.validation.network import IsEmail
import hotqueue
import logging
import logging.handlers
import os
import sys
import yaml

def collect_errors(form):
    errors = []
    join_path = lambda *args: '.'.join(filter(None, args))
    def _collect_errors(f, p=''):
        if f.errors:
            errors.append((join_path(p,f.name), f.errors))
        for c in f.children:
            _collect_errors(c, join_path(p,f.name))
    _collect_errors(form)
    return errors

RequiredString = String.using(validators=[Present()])


class EmailMessageForm(Form):

    subject = RequiredString
    body = RequiredString
    from_email = RequiredString.using(validators=[IsEmail()])
    recipients = (List.using(validators=[Present(), HasAtLeast(minimum=1)])
                      .of(String.named('recipient').using(validators=[IsEmail()])))
    alternatives = (List.using(optional=True)
                        .of(Dict.of(String.named('content'), String.named('mime'))))


def send(mail, connection, logger=None):
    """Send mail which should be in following format:
        >>> mail = {
        ... 'subject': 'SPAM',
        ... 'body': 'spam spam spam',
        ... 'from_email': 'spammer@example.com',
        ... 'recipients': ['recipient1@example.com', 'recipient@example.com'],
        ... 'alternatives': [{
        ...     'content': '<html><body><ul><li>spam</li><li>spam</li></ul></body></html>',
        ...     'mime': 'text/html'
        ... }])}
        >>> send(mail, connection, logger)
    """
    form = EmailMessageForm(mail)
    if form.validate():
        message_data = form.value
        for recipient in message_data.pop('recipients'):
            alternatives = [(a['content'], a['mime']) for a in message_data.pop('alternatives')]
            message = EmailMultiAlternatives(to=[recipient], alternatives=alternatives, **message_data)
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


class ConfigForm(Form):

    hostname = String
    redis = Dict.of(RequiredString.named('host'),
                    Integer.named('port').using(validators=[Present()]),
                    String.named('password').using(optional=True),
                    RequiredString.named('mail_queue'))
    mailing = Dict.of(RequiredString.named('host'),
                      Integer.named('port').using(validators=[Present()]),
                      RequiredString.named('username'),
                      RequiredString.named('password'),
                      RequiredString.named('use_tls'))
    logging = Dict.of(Enum.named('level').valued('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                      Boolean.named('console'),
                      Boolean.named('syslog'),
                      Boolean.named('email'),
                      List.named('admins').of(String.named('admin').using(validators=[IsEmail()])))


def load_config(path=None):
    defaults = {
        'hostname': 'localhost',
        'redis': {
            'host': 'localhost',
            'port': '6379',
            'password': '',
            'mail_queue': 'mail-machine',
        },
        'mailing': {
            'host': None,
            'port': None,
            'username': None,
            'password': None,
            'use_tls': True,
        },
        'logging': {
            'level': 'DEBUG',
            'console': True,
            'syslog': True,
            'email': True,
            'admins': None,
        }
    }

    if path:
        config = yaml.load(open(path))
        for section, default in defaults.items():
            if section in config:
                value = config[section]
                if isinstance(default, dict):
                    for option in default.keys():
                        if option in value:
                            defaults[section][option] = value[option]
                else:
                    defaults[section] = value
    form = ConfigForm.named('form')(defaults)
    if not form.validate():
        errors = collect_errors(form)
        raise ValueError('Config validation error:\n%s' % '\n'.join('%s: %s' % (f,e) for f,e in errors))
    return form.value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mail machine arguments')
    default_config = '/etc/mail-machine.yaml'
    parser.add_argument('-c', '--config', help='Specify configuration file',
                        default=default_config if os.path.exists(default_config) else None)
    args = parser.parse_args()
    config = load_config(args.config)
    mc = config['mailing']
    connection = get_connection(mc['host'], mc['port'], username=mc['username'],
                                password=mc['password'], use_tls=mc['use_tls'])

    rc = config['redis']
    mail_queue = hotqueue.HotQueue(rc['mail_queue'], host=rc['host'], port=rc['port'],
                                   password=rc.get('password'))

    lc = config['logging']
    logger = logging.getLogger('mail-machine')
    logger.setLevel(getattr(logging, lc['level']))
    if lc['console']:
        console_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(console_handler)

    if lc['syslog']:
        syslog_handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON)
        logger.addHandler(syslog_handler)

    if lc['email'] and lc['admins']:
        # probably we should use alternative mailing server here
        subject = 'Log message from %s' % config['hostname']
        from_addr = 'logging@%s' % config['hostname']
        smtp_handler = logging.handlers.SMTPHandler((mc['host'], mc['port']), from_addr,
                                                    lc['admins'], subject=subject,
                                                    credentials=(mc['username'], mc['password']),
                                                    secure=() if mc['use_tls'] else None)
        logger.addHandler(smtp_handler)

    send_mails = mail_queue.worker(lambda mail: send(mail, connection, logger))
    send_mails()

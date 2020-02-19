#!/usr/bin/env python
from email_message import PROTOCOL
import yaml
import os

from .forms import collect_errors, ConfigForm


class Loader(yaml.SafeLoader):

    def __init__(self, stream):

        self._root = os.path.split(stream.name)[0]

        super(Loader, self).__init__(stream)

    def include(self, node):

        filename = os.path.join(self._root, self.construct_scalar(node))

        with open(filename, 'r') as f:
            return yaml.load(f, Loader)

Loader.add_constructor('!include', Loader.include)

def load_config(path=None):
    defaults = {
        'redis': {
            'host': 'localhost',
            'port': '6379',
            'password': '',
            'reconnect': True,
            'mail_queue': 'mailmachine',
            'mail_errors_queue': 'mailmachine-errors',
        },
        'mailing': {
            'host': None,
            'port': None,
            'username': None,
            'password': None,
            'protocol': PROTOCOL.TLS,
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
        config = yaml.load(open(path), Loader)
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


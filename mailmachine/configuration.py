#!/usr/bin/env python
import yaml

from .forms import collect_errors, ConfigForm


def load_config(path=None):
    defaults = {
        'hostname': 'localhost',
        'redis': {
            'host': 'localhost',
            'port': '6379',
            'password': '',
            'mail_queue': 'mailmachine',
            'mail_errors_queue': 'mailmachine-errors',
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


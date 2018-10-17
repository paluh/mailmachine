from flatland.schema import Boolean, Dict, Enum, Form, Integer, List, String
from flatland.validation.scalars import Present
from flatland.validation.network import IsEmail
from email_message import PROTOCOL

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


class ConfigForm(Form):

    redis = Dict.of(RequiredString.named('host'),
                    Integer.named('port').using(validators=[Present()]),
                    String.named('password').using(optional=True),
                    RequiredString.named('mail_queue'),
                    Boolean.named('reconnect'),
                    RequiredString.named('mail_errors_queue'))
    mailing = Dict.of(RequiredString.named('host'),
                      Integer.named('port').using(validators=[Present()]),
                      RequiredString.named('username'),
                      RequiredString.named('password'),
                      Enum.named('protocol').valued(PROTOCOL.SSL, PROTOCOL.TLS, PROTOCOL.PLAIN))
    logging = Dict.of(Enum.named('level').valued('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                      Boolean.named('console'),
                      Boolean.named('syslog'),
                      Boolean.named('email'),
                      List.named('admins').of(String.named('admin').using(validators=[IsEmail()])))


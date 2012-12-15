from flatland.schema import Boolean, Dict, Enum, Form, Integer, List, Scalar, String
from flatland.validation.containers import HasAtLeast
from flatland.validation.scalars import Present
from flatland.validation.network import IsEmail

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


class BinaryData(Scalar):
    """peccata mortalia - feed binary data into textarianin"""

    def set(self, value):
        self.raw = self.value = value
        return True

    @property
    def u(self):
        raise Exception('You don\'t want to see this...')

    def serialize(self):
        raise Exception('You don\'t want to serialize this...')


class EmailMessageForm(Form):

    subject = RequiredString
    body = RequiredString
    from_email = RequiredString.using(validators=[IsEmail()])
    recipients = (List.using(validators=[Present(), HasAtLeast(minimum=1)])
                      .of(String.named('recipient').using(validators=[IsEmail()])))
    alternatives = (List.using(optional=True)
                        .of(Dict.of(String.named('content'),
                                    Enum.named('mime').valued('text/html',))))
    attachments = (List.using(optional=True)
                       .of(Dict.of(String.named('file_name'),
                                   BinaryData.named('content'),
                                   Enum.named('mime').valued('text/html', 'application/pdf'))))
    sent = Integer.using(optional=True)

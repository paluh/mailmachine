from .logging import EnqueueMailLoggingHandler, ImmediateMailLoggingHandler
from .mail import enqueue, send
from .queue import MailQueue

__all__ = ['enqueue', 'EnqueueMailLoggingHandler', 'ImmediateMailLoggingHandler',
           'MailQueue', 'send']

__version__ = '1.0'

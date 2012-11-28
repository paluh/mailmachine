import unittest

import machine


class EmailFormTestCase(unittest.TestCase):

    def test_message_validation(self):
        recipients = ['recipient1@example.com', 'recipient@example.com']
        form = machine.EmailMessageForm({
            'subject': 'SPAM',
            'body': 'spam spam spam',
            'from_email': 'spammer@example.com',
            'recipients': recipients,
        })
        self.assertTrue(form.validate())
        self.assertEqual([r.value for r in form['recipients']], recipients)

    def test_message_validation_checks_recipients_emails_format(self):
        form = machine.EmailMessageForm({
            'subject': 'SPAM',
            'body': 'spam spam spam',
            'from_email': 'spammer@example.com',
            'recipients': ['recipient1@example.com', 'wrong-email-format'],
        })
        self.assertFalse(form.validate())
        self.assertTrue(len(form['recipients'][1].errors) > 0)

    def test_message_validation_requires_recipients(self):
        form = machine.EmailMessageForm({
            'subject': 'SPAM',
            'body': 'spam spam spam',
            'from_email': 'spammer@example.com',
        })
        self.assertFalse(form.validate())
        self.assertTrue(len(form['recipients'].errors) > 0)

    def test_message_with_alternatives_validation(self):
        alternative = {
            'content': '<html><body><ul><li>spam</li><li>spam</li></ul></body></html>',
            'mime': 'text/html'
        }
        form = machine.EmailMessageForm({
            'subject': 'SPAM',
            'body': 'spam spam spam',
            'from_email': 'spammer@example.com',
            'recipients': ['recipient1@example.com', 'recipient@example.com'],
            'alternatives': [alternative],
        })
        self.assertTrue(form.validate())
        self.assertEqual(form['alternatives'][0].value, alternative)

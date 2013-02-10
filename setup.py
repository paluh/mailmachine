try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

REQUIREMENTS = [
    'email_message >= 2012-9-1',
    'great_justice >= 2012.6.8',
    'hotqueue',
    'flatland',
    'pyyaml',
    'simplejson',
]
DEPENDENCY_LINKS = [
    'git+git://github.com/paluh/email-message.git#egg=email_message-2012-9-1',
    'git+git://github.com/paluh/great-justice.git#egg=great_justice-2012.6.8',
]
setup(
    name='mailmachine',
    author='Tomasz Rybarczyk',
    author_email='paluho@gmail.com',
    classifiers=[
        'Programming Language :: Python'
    ],
    description='',
    dependency_links=DEPENDENCY_LINKS,
    install_requires=REQUIREMENTS,
    url='https://bitbucket.org/nadaje/mailmachine',
    packages=['mailmachine'],
    scripts=['scripts/mailmachined', 'scripts/mailmachinectl'],
    zip_safe=False,
    version = '2013.2.3',
)

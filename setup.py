try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
]

REQUIREMENTS = [
    'email-message == 1.1.1',
    'great-justice-with-logging == 1.0.3',
    'hotqueue',
    'flatland == 0.8',
    'pyyaml',
    'pygments',
    'simplejson',
]
DEPENDENCY_LINKS = [
    'git+git://github.com/paluh/email-message.git@1.1.1#egg=email-message-1.1.1',
    'git+git://github.com/paluh/great-justice-with-logging.git@1.0.3#egg=great-justice-with-logging-1.0.3',
]
setup(
    name='mailmachine',
    author='Tomasz Rybarczyk',
    author_email='paluho@gmail.com',
    classifiers=CLASSIFIERS,
    description='Simple, single threaded mailing worker.',
    dependency_links=DEPENDENCY_LINKS,
    install_requires=REQUIREMENTS,
    url='https://github.com/paluh/mailmachine',
    packages=['mailmachine'],
    scripts=['scripts/mailmachined', 'scripts/mailmachinectl'],
    zip_safe=False,
    version = '1.2.0',
)

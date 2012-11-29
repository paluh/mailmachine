try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='mailmessage',
    author='Tomasz Rybarczyk',
    author_email='paluho@gmail.com',
    classifiers=[
        'Programming Language :: Python'
    ],
    description='',
    url='https://bitbucket.org/nadaje/mailmachine',
    packages=['mailmachine'],
    scripts=['scripts/mailmachined', 'scripts/mailmachinectl'],
    zip_safe=False,
    version = '2012.11.1',
)

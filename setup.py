# -*- coding: utf-8 -*-
"""
aeauth
==========


Quick links
-----------

- `User Guide <http://code.scotchmedia.com/aeauth>`_
- `Repository <http://github.com/scotch/aeauth>`_
- `Issue Tracker <https://github.com/scotch/aeauth/issues>`_

"""
from setuptools import setup

setup(
    name = 'aeauth',
    version = '0.1.0',
    license = 'Apache Software License',
    url = 'http://code.scotchmedia.com/aeauth',
    description = "Adds Multi-Provider Authentication to Google App Engine",
    long_description = __doc__,
    author = 'Kyle Finley',
    author_email = 'kyle.finley@gmail.com',
    zip_safe = True,
    platforms = 'any',
    packages = [
        'aeauth',
        'aeauth.strategies',
    ],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'aecore',
        'python-gflags',
        'google-api-python-client',
    ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
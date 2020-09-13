#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup

version = '0.1'
description = u"Django multiple schemas per-database, app-based router"
long_description = description
try:
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
except:
pass

classifiers = ['Environment :: Plugins',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
'Topic :: Software Development :: Libraries :: Python Modules',]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-pg-schema',
    version = version,
    description = description,
    long_description = long_description,
    classifiers = classifiers,
    keywords = 'django apps routers schema multi db ',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    long_description=README,
    url='https://github.com/jelitox/django_async',
    author='Jesus Lara',
    author_email='jesuslara@phenobarbital.info',
    package_dir = {'pgschema': 'pgschema'},
    url = 'https://github.com/avelino/django-routers/',
    download_url = "https://github.com/avelino/django-routers/tarball/master",
    install_requires=[
        'Django >= 3.1.0',
        'psycopg2',
    ],
    zip_safe=False,
)

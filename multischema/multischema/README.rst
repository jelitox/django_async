=====
Django-pg-schema
=====

Django-pg-schema is a simple Django DBRouter for using schema-based apps for django.

Detailed documentation is in the "docs" directory.

 Install
-----------

    pip install django-pg-schema

Quick start
-----------

1. Add "pg-schema" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'navigator.pgschema',
    ]

2. Include pg-schema into Database Routers settings like this::

   DATABASE_ROUTERS = [ 'navigator.pgschema.routers.schemaRouter' ]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# default settings for database schema router
DATABASE_ROUTERS = [ 'navigator.pgschema.routers.schemaRouter' ]
DATABASE_STATEMENT_TIMEOUT = 60000 # on milliseconds
DATABASE_COLLATION = 'UTF8'
DEBUG_SQL = True
DATABASE_TZ = 'UTC'

from django.db.backends.utils import CursorWrapper, CursorDebugWrapper
from django.db.backends.postgresql.base import *
from django.conf import settings
from time import time
from .exceptions import DatabaseWriteDenied

try:
    DATABASES = settings.DATABASES
    DATABASE_STATEMENT_TIMEOUT = settings.DATABASE_STATEMENT_TIMEOUT
    DATABASE_COLLATION = settings.DATABASE_COLLATION
    DEBUG_SQL = settings.DEBUG_SQL
    DATABASE_TZ = settings.DATABASE_TZ
except Exception as e:
    from .settings import DATABASE_STATEMENT_TIMEOUT, DATABASE_COLLATION, DEBUG_SQL, DATABASE_TZ

from logging import getLogger
logger = getLogger('django.db.backends')

class DatabaseWrapper(DatabaseWrapper):
    """Database wrapper for override postgreSQL Backend."""

    params = None
    readonly = False
    name = None
    schema = None

    def __init__(self, *args, **kwargs):
        """Override init method."""
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.params = args[0]
        self.name = args[1]
        try:
            self.schema = args[0]['SCHEMA']
        except KeyError:
            self.schema = 'public'

    def get_new_connection(self, conn_params):
        """Override Database Connection for set Read-Only Connections."""
        conn = super(DatabaseWrapper, self).get_new_connection(conn_params)
        try:
            readonly = self.params['PARAMS']
        except KeyError:
            readonly = None
        if readonly is not None and readonly['readonly'] is True:
            conn.set_session(readonly = True)
            self.readonly = True
        return conn

    def _cursor(self, name=None):
        cursor = super(DatabaseWrapper, self)._cursor(name=None)
        cursor.execute("SET CLIENT_ENCODING TO '%s'" % DATABASE_COLLATION)
        cursor.execute("SET NAMES '%s'" % DATABASE_COLLATION)
        cursor.execute("SET STATEMENT_TIMEOUT=%s" % DATABASE_STATEMENT_TIMEOUT)
        if DATABASE_TZ:
            cursor.execute("SET timezone='%s'" % DATABASE_TZ)
        #if debug_sql is not None:
        #    cursor.execute("SET log_statement = 'all'")
        # enable schema
        cursor.execute("SET search_path to {},troc,public".format(self.schema))
        return cursor


class ReadOnlyCursorWrapper(object):
    """
    This is a wrapper for a database cursor.

    This sits between django's own wrapper at
    `django.db.backends.util.CursorWrapper` and the database specific cursor at
    `django.db.backends.*.base.*CursorWrapper`. It overrides two specific
    methods: `execute` and `executemany`. If the site is in read-only mode,
    then the SQL is examined to see if it contains any write actions. If a
    write is detected, an exception is raised.

    Raises a DatabaseWriteDenied exception if writes are disabled.
    """
    readonly = False
    SQL_WRITE_BLACKLIST = (
        # Data Definition
        'CREATE', 'ALTER', 'RENAME', 'DROP', 'TRUNCATE',
        # Data Manipulation
        'INSERT INTO', 'UPDATE', 'REPLACE', 'DELETE FROM',
    )

    def __init__(self, cursor, db):
        self.cursor = cursor
        self.readonly = db.readonly
        logger.debug(
            "Database read-only status is %s" % self.readonly
            )
        self.db = db

    def execute(self, sql, params=()):
        # Check the SQL
        try:
            if self.readonly and self._write_sql(sql):
                logger.debug(
                    "Database read-only for database %s is %s" % (self.db.name, self.readonly)
                )
                raise DatabaseWriteDenied("Read-Only Database: %s" % self.db.name)
                return None
            else:
                return self.cursor.execute(sql, params)
        except psycopg2.IntegrityError as ie:
            print('Error: {}'.format(ie))
            print('Query: {}'.format(sql))

    def executemany(self, sql, param_list):
        # Check the SQL
        if self.readonly and self._write_sql(sql):
            raise DatabaseWriteDenied("Read-Only Database: %s" % self.db.name)
        return self.cursor.executemany(sql, param_list)

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

    def _write_sql(self, sql):
        return sql.startswith(self.SQL_WRITE_BLACKLIST)


    @property
    def _last_executed(self):
        return getattr(self.cursor, '_last_executed', '')

class CursorWrapper(CursorWrapper):
    def __init__(self, cursor, db):
        self.cursor = ReadOnlyCursorWrapper(cursor, db)
        self.db = db

# Redefine CursorDebugWrapper because we want it to inherit from *our*
# CursorWrapper instead of django.db.backends.util.CursorWrapper
class CursorDebugWrapper(CursorWrapper):

    def execute(self, sql, params=()):
        start = time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = time()
            duration = stop - start
            sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            self.db.queries.append({
                'sql': sql,
                'time': "%.3f" % duration,
            })
            logger.debug(
                '(%.3f) %s; args=%s',
                duration, sql, params,
                extra={'duration': duration, 'sql': sql, 'params': params}
            )

    def executemany(self, sql, param_list):
        start = time()
        try:
            return self.cursor.executemany(sql, param_list)
        finally:
            stop = time()
            duration = stop - start
            self.db.queries.append({
                'sql': '%s times: %s' % (len(param_list), sql),
                'time': "%.3f" % duration,
            })
            logger.debug(
                '(%.3f) %s; args=%s',
                duration, sql, param_list,
                extra={'duration': duration, 'sql': sql, 'params': param_list}
            )

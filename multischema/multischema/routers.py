"""Class definition for Database Routing."""
from django.urls import resolve
from django.apps import apps
from django.conf import settings
from django.db import router, connections
import sys
import threading
from django.http import Http404


request_cfg = threading.local()


DEFAULT_DB_ALIAS = 'default'
USER_APPS = settings.DATABASES.keys()
SYSTEM_APPS = [ 'admin', 'auth', 'contenttypes', 'dashboard', 'sessions', 'sites', 'silk', 'social_django', 'notifications', 'social_django' ]
SYSTEM_TABLES = [ 'auth_user', 'auth_group', 'auth_permission', 'auth_user_groups', 'auth_user_user_permissions', 'social_auth_usersocialauth' ]

class schemaRouter(object):
    """A router to control troc db operations."""

    db = None
    index = len(USER_APPS)

    def __init__(self):
        """Get information about databases."""
        self.db = settings.DATABASES

    def _multi_db(self, model):
        from django.conf import settings
        #print(model._meta.db_table)
        if hasattr(request_cfg, 'db'):
            print(request_cfg.db)
            if request_cfg.db in self.db.keys():
                return request_cfg.db
            else:
                raise Http404
        else:
            return DEFAULT_DB_ALIAS

    def db_for_read(self, model, **hints):
        """Point all operations on app1 models to 'db_app1'."""
        if model._meta.app_label in SYSTEM_APPS:
            return DEFAULT_DB_ALIAS
        if model._meta.app_label in self.db.keys():
            return model._meta.app_label
        else:
            return self._multi_db()
        return None

    def db_for_write(self, model, **hints):
        """Point all operations on app1 models to 'db_app1'."""
        if model._meta.app_label in SYSTEM_APPS or model._meta.db_table in SYSTEM_TABLES:
            return DEFAULT_DB_ALIAS
        if model._meta.app_label in self.db.keys():
            #db_table = 'schema\".\"tablename'
            try:
                readonly = self.db[model._meta.app_label]['PARAMS']['readonly']
                if readonly:
                    # Read Only Database
                    return False
                else:
                    table = model._meta.db_table
                    if table.find('.') == -1:
                        schema = model._meta.app_label
                        model._meta.db_table = '{}\".\"{}'.format(schema, table)
                    return self._multi_db(model)
            except KeyError:
                table = model._meta.db_table
                #print(table.find('.'))
                if table.find('.') == -1:
                    schema = model._meta.app_label
                    model._meta.db_table = '{}\".\"{}'.format(schema, table)
                    #model._meta.db_table = '{}.{}'.format(schema, table)
                return self._multi_db(model)
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation if a model in app1 is involved."""
        if obj1._meta.app_label in [ 'auth' ] or obj2._meta.app_label in [ 'auth' ]:
            """ Can made migrations with AUTH model """
            return True
        if obj1._meta.app_label in self.db.keys() or obj2._meta.app_label in self.db.keys():
            try:
                db1 = self.db[obj1._meta.app_label]['NAME']
                db2 = self.db[obj2._meta.app_label]['NAME']
            except KeyError:
                return True
            if db1 == db2:
                """ Both DB are the same """
                return True
            else:
                return False
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """Make sure the app1 only appears in the 'app1' database."""
        if app_label in SYSTEM_APPS:
            db == 'default'
            return True
        if db == 'default':
            #print('APP LABEL: %s DB: %s' % (app_label, b))
            if app_label in self.db.keys():
                # cannot run migration of app models onto default database
                db = app_label
                return True
            elif model and model._meta.app_label in self.db.keys():
                db = app_label
                return False
            else:
                return None
        if model and app_label in self.db.keys():
            try:
                readonly = self.db[app_label]['PARAMS']['readonly']
                if readonly:
                    return False
                else:
                    return True
            except KeyError:
                return True
        return None

    def ensure_schema(self):
        """
        Ensures the table exists and has the correct schema.
        """
        if self.Migration._meta.db_table in self.connection.introspection.get_table_list(self.connection.cursor()):
            return
        if router.allow_migrate(self.connection, self.Migration):
            with self.connection.schema_editor() as editor:
                editor.create_model(self.Migration)

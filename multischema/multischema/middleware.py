import django
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404


if django.VERSION >= (1, 10, 0):
    MIDDLEWARE_MIXIN = django.utils.deprecation.MiddlewareMixin
else:
    MIDDLEWARE_MIXIN = object


"""
    The schemaRouter router middleware.

    Add this to your middleware, for example:

    MIDDLEWARE += ['navigator.pgschema.routers.schemaRouterMiddleware']
"""
class schemaRouterMiddleware(MIDDLEWARE_MIXIN):
    def __init__(self, get_response):
        self.get_response = get_response

    def set_schema(self, request):
        #schema = tenant_schema_from_request(request)
        print(request)
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path to {schema},public")

    def __call__(self, request):
        print(request)
        return self.get_response(request)

    def process_view(self, request, view_func, args, kwargs):
        if 'db' in kwargs:
            request_cfg.db = kwargs['db']
            request.SELECTED_DATABASE = request_cfg.db

    def process_response(self, request, response):
        if hasattr(request_cfg, 'db'):
            del request_cfg.db
        return response

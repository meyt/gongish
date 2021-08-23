import sys
import inspect
import functools

from .request import Request
from .response import Response
from .exceptions import (
    HTTPStatus,
    HTTPSuccess,
    HTTPNotFound,
    HTTPBadRequest,
    HTTPInternalServerError,
)
from .response_formatters import ResponseFormattersMixin
from .static import StaticHandlerMixin

ROUTE_VERB = 0
ROUTE_ARG = 1
ROUTE_WILDCARD = 2
http_success = HTTPSuccess().status


class RouterMixin(StaticHandlerMixin, ResponseFormattersMixin):
    __request_factory__ = Request
    __response_factory__ = Response
    __route_argument_char__ = ":"

    def __init__(self):
        self.request = None
        self.response = None
        self.verbs = set()
        self.paths = set()
        self.routes = dict()

    def on_begin_request(self):
        """ Hook """
        pass

    def on_begin_response(self):
        """ Hook """
        pass

    def on_end_response(self):
        """ Hook """
        pass

    def on_error(self, exc: HTTPStatus):
        """ Hook """
        pass

    def __getattr__(self, key):
        formatter = super().__getattribute__(f"format_{key}")
        return functools.partial(self.route, formatter=formatter)

    def chunked(self, trailer_field=None, trailer_value=None):
        """
        http://tools.ietf.org/html/rfc2616#section-14.40
        http://tools.ietf.org/html/rfc2616#section-14.41
        """
        app = self

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                nonlocal trailer_field, trailer_value, app
                app.response.headers["transfer-encoding"] = "chunked"
                if trailer_field:
                    app.response.headers["trailer"] = trailer_field

                result = func(*args, **kwargs)
                try:
                    while True:
                        chunk = next(result)
                        yield f"{len(chunk)}\r\n{chunk}\r\n"

                except StopIteration:
                    yield "0\r\n"
                    if trailer_field and trailer_value:
                        yield f"{trailer_field}: {trailer_value}\r\n"
                    yield "\r\n"

                except Exception as ex:
                    exstr = str(ex)
                    yield f"{len(exstr)}\r\n{exstr}"
                    yield "0\r\n\r\n"

            return wrapper

        if callable(trailer_field):
            func = trailer_field
            trailer_field = None
            return decorator(func)

        return decorator

    def route(self, path, formatter=None, **kwargs):
        def decorator(func):
            app = self
            funcname = func.__name__.lower()

            # Set formatter
            func.__gongish_formatter__ = functools.partial(
                formatter or self.__class__.__default_formatter__, **kwargs
            )

            # Get parameters
            func.__gongish_route_params__ = tuple(
                [
                    (param.name, param.annotation)
                    for param in inspect.signature(func).parameters.values()
                ]
            )

            # Distribute
            resources = path.split("/")
            parent = app.routes
            for resource in resources:
                firstchar = resource[:1]
                if firstchar == app.__route_argument_char__:
                    resource = ROUTE_ARG

                elif firstchar == "*":
                    resource = ROUTE_WILDCARD

                if resource not in parent.keys():
                    parent[resource] = {}

                parent = parent[resource]

            if ROUTE_VERB not in parent.keys():
                parent[ROUTE_VERB] = {funcname: func}
            else:
                parent[ROUTE_VERB][funcname] = func

            self.paths.add(path)
            self.verbs.add(funcname)

        return decorator

    def handle_exception(self, exc, start_response):
        if isinstance(exc, HTTPStatus):
            exc_ = exc
            exc_info = None

        else:
            exc_ = HTTPInternalServerError()
            exc_info = sys.exc_info()
            self.__logger__.exception(exc_.text, exc_info=True)

        exc_.setup_response(app=self)

        self.on_error(exc_)  # hook

        self.response.prepare_to_start()

        start_response(
            exc_.status, list(self.response.headers.items()), exc_info
        )

        return self.response.start()

    def dispatch(self, path: str, verb: str):
        """
        Dispatch path and return handler function
        """

        # Split path
        resources = path.split("/")
        route = self.routes
        route_keys = route.keys()
        route_args = []
        steps = 0
        for resource in resources:
            if resource in route_keys:
                route = route[resource]
                route_keys = route.keys()
                steps += 1

            elif ROUTE_ARG in route_keys:
                # Extract arguments
                route = route[ROUTE_ARG]
                route_keys = route.keys()
                route_args.append(resource)
                steps += 1

            elif ROUTE_WILDCARD in route_keys:
                if ROUTE_WILDCARD in route:
                    route = route[ROUTE_WILDCARD]
                route_keys = (ROUTE_WILDCARD,)
                route_args.append(resource)
                steps += 1

        if steps != len(resources) or verb not in route[ROUTE_VERB].keys():
            raise HTTPNotFound

        handler = route[ROUTE_VERB][verb]

        # Validate parameters
        for idx, param in enumerate(handler.__gongish_route_params__):
            name, annotation = param

            if annotation == inspect._empty:
                continue

            # Call the annotation
            try:
                route_args[idx] = annotation(route_args[idx])

            except Exception:
                raise HTTPBadRequest(f"Invalid Parameter `{name}`")

        return handler, route_args

    def __call__(self, environ, start_response):
        """ Application WSGI entry """
        self.request = request = self.__request_factory__(environ)
        self.response = response = self.__response_factory__(app=self)
        try:
            self.on_begin_request()  # hook

            # Call handler
            handler, route_args = self.dispatch(request.path, request.verb)
            response.body = handler(*route_args)
            response.status = http_success

            # Format response
            handler.__gongish_formatter__(request, response)

            response.prepare_to_start()

        except Exception as exc:
            return self.handle_exception(exc, start_response)

        self.on_begin_response()  # hook

        # Cookies
        cookie = request.cookies.output()
        if cookie:
            for line in cookie.split("\r\n"):
                response.headers.add(*line.split(": ", 1))

        start_response(response.status, list(response.headers.items()))

        return response.start()

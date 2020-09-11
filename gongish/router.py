import sys
import inspect

from functools import partial

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

ROUTE_VERB = 0
ROUTE_ARG = 1
http_success = HTTPSuccess().status


class RouterMixin(ResponseFormattersMixin):
    __request_factory__ = Request
    __response_factory__ = Response
    __route_argument_char__ = ":"

    def __init__(self):
        self.request = None
        self.response = None
        self.routes = {}

    def begin_request(self):
        """ Hook """
        pass

    def begin_response(self):
        """ Hook """
        pass

    def end_response(self):
        """ Hook """
        pass

    def on_error(self, exc: HTTPStatus):
        """ Hook """
        pass

    def __getattr__(self, key):
        formatter = super().__getattribute__(f"format_{key}")
        return partial(self.route, formatter=formatter)

    def route(self, path, formatter=None, **kwargs):
        def decorator(func):
            app = self

            # Set formatter
            func.__gongish_formatter__ = partial(
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

                if resource.startswith(app.__route_argument_char__):
                    resource = ROUTE_ARG

                if resource not in parent.keys():
                    parent[resource] = {}

                parent = parent[resource]

            if ROUTE_VERB not in parent.keys():
                parent[ROUTE_VERB] = {func.__name__: func}
            else:
                parent[ROUTE_VERB][func.__name__] = func

        return decorator

    def handle_exception(self, exc, start_response):
        if isinstance(exc, HTTPStatus):
            exc_ = exc
            exc_info = None

        else:
            exc_ = HTTPInternalServerError()
            exc_info = sys.exc_info()
            self.__logger__.exception(exc_.text, exc_info=True)

        if exc_.__keep_headers__:
            self.response.headers.update(exc_.headers)
        else:
            self.response.headers = exc_.headers

        self.response.charset = "utf-8"
        self.response.type = "plain/text"
        self.response.body = exc_.render(debug=self.config.debug)

        self.on_error(exc_)  # hook

        body = self.response.conclude()

        start_response(
            exc_.status, list(self.response.headers.items()), exc_info
        )

        self.end_response()  # hook

        return body

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
        self.response = response = self.__response_factory__()
        self.begin_request()  # hook

        try:
            # Call handler
            handler, route_args = self.dispatch(request.path, request.verb)
            response.body = handler(*route_args)
            response.status = http_success

            # Format response
            handler.__gongish_formatter__(request, response)

        except Exception as exc:
            return self.handle_exception(exc, start_response)

        self.begin_response()  # hook

        # Cookies
        cookie = request.cookies.output()
        if cookie:
            for line in cookie.split("\r\n"):
                response.headers.add(*line.split(": ", 1))

        body = response.conclude()

        start_response(response.status, list(response.headers.items()))

        self.end_response()  # hook
        return body

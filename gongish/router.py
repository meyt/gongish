import functools
import inspect
import sys
from contextvars import ContextVar

from .exceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
    HTTPNotFound,
    HTTPStatus,
    HTTPSuccess,
)
from .helpers import WordRouter
from .request import Request
from .response import Response
from .response_formatters import ResponseFormattersMixin
from .static import StaticHandlerMixin

http_success = HTTPSuccess().status


class RouterMixin(StaticHandlerMixin, ResponseFormattersMixin):
    request_factory = Request
    response_factory = Response
    _route_argument_char = ":"
    _request_var = ContextVar("request", default=None)
    _response_var = ContextVar("response", default=None)

    def __init__(self):
        self.verbs = set()
        self.paths = set()
        self.wordrouter = WordRouter()
        self._clear_context()

    @property
    def request(self):
        return self.__class__._request_var.get()

    @property
    def response(self):
        return self.__class__._response_var.get()

    @classmethod
    def _clear_context(cls):
        cls._request_var.set(None)
        cls._response_var.set(None)
        cls._current_app_var.set(None)

    @classmethod
    def _create_context(cls, environ):
        request = cls.request_factory(environ)
        response = cls.response_factory()
        cls._request_var.set(request)
        cls._response_var.set(response)
        return request, response

    def on_begin_request(self):
        """Hook"""
        pass

    def on_begin_response(self):
        """Hook"""
        pass

    def on_end_response(self):
        """Hook"""
        pass

    def on_error(self, exc: HTTPStatus):
        """Hook"""
        pass

    def __getattr__(self, key):
        try:
            formatter = super().__getattribute__(f"format_{key}")
            return functools.partial(self.route, formatter=formatter)
        except AttributeError:
            try:
                return super().__getattribute__(key)
            except AttributeError:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute "
                    f"'format_{key}' or '{key}'"
                )

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

    def route(self, path, formatter=None, verbs=None, **kwargs):
        def decorator(fn):
            for verb in verbs if verbs else (fn.__name__,):
                verb = verb.lower()

                # Set formatter
                fn._gongish_formatter = functools.partial(
                    formatter or self.__class__.default_formatter, **kwargs
                )

                # Get parameters
                fn._gongish_route_params = tuple(
                    [
                        (param.name, param.annotation)
                        for param in inspect.signature(fn).parameters.values()
                    ]
                )

                # Distribute
                self.wordrouter.add(verb + path, fn)
                self.paths.add(path)
                self.verbs.add(verb)

        return decorator

    def handle_exception(self, exc, start_response):
        if isinstance(exc, HTTPStatus):
            exc_ = exc
            exc_info = None

        else:
            exc_ = HTTPInternalServerError()
            exc_info = sys.exc_info()
            self._log.exception(exc_.text, exc_info=True)

        exc_.setup_response(app=self)

        self.on_error(exc_)  # hook

        self.response.prepare_to_start()

        start_response(
            exc_.status,
            list(self.response.headers.items()),
            exc_info,
        )

        return self._process_response()

    def _process_streaming_response(self):
        # encode if required
        resp = self.response
        if resp.charset and not isinstance(resp._firstchunk, bytes):
            yield resp._firstchunk.encode(resp.charset)
            for chunk in resp.body:
                yield chunk.encode(resp.charset)

        else:
            yield resp._firstchunk
            for chunk in resp.body:
                yield chunk

        self.on_end_response()  # hook
        self._clear_context()

    def _process_response(self):
        if self.response._firstchunk is not None:
            return self._process_streaming_response()

        r = self.response.body
        self.on_end_response()  # hook
        self._clear_context()
        return r

    def dispatch(self, path: str, verb: str):
        """
        Dispatch path and return handler function
        """

        handler, route_args = self.wordrouter.dispatch(verb + path)
        if not handler:
            raise HTTPNotFound

        # Validate parameters
        for idx, param in enumerate(handler._gongish_route_params):
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
        """Application WSGI entry"""
        self.__class__._current_app_var.set(self)
        request, response = self._create_context(environ)

        try:
            self.on_begin_request()  # hook

            # Call handler
            handler, route_args = self.dispatch(request.path, request.verb)
            response.body = handler(*route_args)
            response.status = http_success

            # Format response
            handler._gongish_formatter(request, response)

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
        return self._process_response()

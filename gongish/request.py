import cgi
import wsgiref.util as wsgiutil

try:
    import ujson as json
except ImportError:  # pragma: no cover
    import json

from http import cookies
from urllib.parse import parse_qs

from gongish.helpers import HeaderSet, LazyAttribute
from gongish.exceptions import HTTPBadRequest


def getcgifieldvalue(field):
    return (
        field.value
        if isinstance(field, cgi.MiniFieldStorage)
        or (isinstance(field, cgi.FieldStorage) and not field._binary_file)
        else field
    )


class RequestForm(dict):
    def __init__(self, environ, contenttype, contentlength):
        if contenttype == "application/json":
            if contentlength is None:
                raise HTTPBadRequest

            fp = environ["wsgi.input"]
            try:
                super().__init__(json.load(fp))
                return

            except (ValueError, TypeError):
                raise HTTPBadRequest("Cannot parse the request")

        if "QUERY_STRING" not in environ:
            environ["QUERY_STRING"] = ""

        try:
            storage = cgi.FieldStorage(
                fp=environ["wsgi.input"],
                environ=environ,
                strict_parsing=False,
                keep_blank_values=True,
            )

        except (TypeError, ValueError):
            raise HTTPBadRequest("Cannot parse the request")

        super().__init__()
        if storage.list is None or not len(storage.list):
            return

        for k in storage:
            v = storage[k]
            if isinstance(v, list):
                self[k] = [getcgifieldvalue(i) for i in v]
            else:
                self[k] = getcgifieldvalue(v)

    def __getattr__(self, key):
        if key not in self:
            return None
        return self[key]


class Request:
    def __init__(self, environ):
        self.environ = environ

    @LazyAttribute
    def verb(self):
        return self.environ["REQUEST_METHOD"].lower()

    @LazyAttribute
    def path(self):
        return self.environ["PATH_INFO"]

    @LazyAttribute
    def fullpath(self):
        """ Request full URI (includes query string) """
        return wsgiutil.request_uri(self.environ, include_query=True)

    @LazyAttribute
    def contentlength(self):
        v = self.environ.get("CONTENT_LENGTH")
        return None if not v or not v.strip() else int(v)

    @LazyAttribute
    def contenttype(self):
        contenttype = self.environ.get("CONTENT_TYPE")
        if contenttype:
            return contenttype.split(";")[0]
        return None

    @LazyAttribute
    def query(self):
        if "QUERY_STRING" not in self.environ:
            return {}

        return {
            k: v[0] if len(v) == 1 else v
            for k, v in parse_qs(
                self.environ["QUERY_STRING"],
                keep_blank_values=True,
                strict_parsing=False,
            ).items()
        }

    @LazyAttribute
    def form(self):
        return RequestForm(self.environ, self.contenttype, self.contentlength)

    @LazyAttribute
    def cookies(self):
        result = cookies.SimpleCookie()
        if "HTTP_COOKIE" in self.environ:
            result.load(self.environ["HTTP_COOKIE"])
        return result

    @LazyAttribute
    def scheme(self):
        """Request Scheme (http|https)
        """
        return wsgiutil.guess_scheme(self.environ)

    @LazyAttribute
    def headers(self):
        return HeaderSet().load_from_wsgi_environ(self.environ)

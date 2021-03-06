import traceback

from gongish.helpers import HeaderSet


class HTTPStatus(Exception):
    code = None
    text = None
    headers = HeaderSet()
    __keep_headers__ = False
    __keep_body__ = True

    @property
    def status(self):
        return f"{self.code} {self.text}"

    def render(self, debug: bool) -> str:
        if not self.__class__.__keep_body__:
            return

        return traceback.format_exc() if debug else self.status


class HTTPKnownStatus(HTTPStatus):
    def __init__(self, status_text=None):
        if status_text is not None:
            self.text = status_text
        super().__init__()


class HTTPBadRequest(HTTPKnownStatus):
    code = 400
    text = "Bad Request"


class HTTPUnauthorized(HTTPKnownStatus):
    code = 401
    text = "Unauthorized"


class HTTPForbidden(HTTPKnownStatus):
    code = 403
    text = "Forbidden"


class HTTPNotFound(HTTPKnownStatus):
    code = 404
    text = "Not Found"


class HTTPMethodNotAllowed(HTTPKnownStatus):
    code = 405
    text = "Method Not Allowed"


class HTTPConflict(HTTPKnownStatus):
    code = 409
    text = "Conflict"


class HTTPGone(HTTPKnownStatus):
    code = 410
    text = "Gone"


class HTTPPreconditionFailed(HTTPKnownStatus):
    code = 412
    text = "Precondition Failed"


class HTTPRedirect(HTTPKnownStatus):
    """
    This is an abstract class for all redirects.
    """

    def __init__(self, location, *args, **kw):
        self.headers["Location"] = location
        super().__init__(*args, **kw)


class HTTPMovedPermanently(HTTPRedirect):
    code = 301
    text = "Moved Permanently"
    __keep_body__ = False


class HTTPFound(HTTPRedirect):
    code = 302
    text = "Found"
    __keep_body__ = False


class HTTPNotModified(HTTPKnownStatus):
    code = 304
    text = "Not Modified"
    __keep_body__ = False


class HTTPInternalServerError(HTTPKnownStatus):
    code = 500
    text = "Internal Server Error"


class HTTPBadGatewayError(HTTPKnownStatus):
    code = 502
    text = "Bad Gateway"


class HTTPSuccess(HTTPKnownStatus):
    code = 200
    text = "OK"
    __keep_headers__ = True


class HTTPCreated(HTTPSuccess):
    code = 201
    text = "Created"
    __keep_headers__ = True


class HTTPAccepted(HTTPSuccess):
    code = 202
    text = "Accepted"
    __keep_headers__ = True


class HTTPNonAuthoritativeInformation(HTTPSuccess):
    code = 203
    text = "Non-Authoritative Information"
    __keep_headers__ = True


class HTTPNoContent(HTTPSuccess):
    code = 204
    text = "No Content"
    __keep_body__ = False
    __keep_headers__ = True


class HTTPResetContent(HTTPSuccess):
    code = 205
    text = "Reset Content"
    __keep_body__ = False
    __keep_headers__ = True


class HTTPPartialContent(HTTPSuccess):
    code = 206
    text = "Partial Content"
    __keep_headers__ = True

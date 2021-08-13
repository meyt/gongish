import types
from .helpers import HeaderSet


class Response:
    def __init__(self, app):
        self.app = app
        self.headers = HeaderSet()
        self.status = "200 OK"
        self.body = None
        self.type = None
        self.charset = None
        self.length = None
        self._firstchunk = None

    @property
    def contenttype(self):
        if not self.type:
            return None

        result = self.type
        if self.charset:
            result += f"; charset={self.charset}"

        return result

    def prepare_to_start(self):
        contenttype = self.contenttype
        if contenttype:
            self.headers["content-type"] = contenttype

        body = self.body
        if isinstance(body, types.GeneratorType):
            # Trying to get at least one element from the generator,
            # to force the method call till the second
            # `yield` statement
            self._firstchunk = next(body)
            if self.length is not None:
                self.headers["content-length"] = str(self.length)
        else:
            if body is None:
                body = []

            elif isinstance(body, (str, bytes)):
                body = [body]

            if self.charset:
                body = [i.encode(self.charset) for i in body]

            self.headers["content-length"] = str(
                sum(len(i) for i in body)
                if self.length is None
                else self.length
            )
            self.body = body

    def startstream(self):
        # encode if required
        if self.charset and not isinstance(self._firstchunk, bytes):
            yield self._firstchunk.encode(self.charset)
            for chunk in self.body:
                yield chunk.encode(self.charset)

        else:
            yield self._firstchunk
            for chunk in self.body:
                yield chunk

        self.app.on_end_response()  # hook

    def start(self):
        if self._firstchunk is not None:
            return self.startstream()

        self.app.on_end_response()  # hook
        return self.body

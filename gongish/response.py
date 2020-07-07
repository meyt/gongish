from .helpers import HeaderSet


class Response:
    def __init__(self):
        self.headers = HeaderSet()
        self.status = "200 OK"
        self.length = None
        self.body = None
        self._type = None
        self._charset = None

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        self._type = val
        self.headers["content-type"] = self.contenttype

    @property
    def charset(self):
        return self._charset

    @charset.setter
    def charset(self, val):
        self._charset = val
        self.headers["content-type"] = self.contenttype

    @property
    def contenttype(self):
        if not self._type:
            return None

        result = self._type
        if self._charset:
            result += f"; charset={self._charset}"

        return result

    def conclude(self):
        body = self.body
        if body is None:
            body = []

        elif isinstance(body, (str, bytes)):
            body = [body]

        if self.charset:
            body = [i.encode(self.charset) for i in body]

        if self.length is None:
            self.length = sum(len(i) for i in body)

        return body

from collections import OrderedDict

content_environ = ("HTTP_CONTENT_TYPE", "HTTP_CONTENT_LENGTH")
content_headers = ("CONTENT_TYPE", "CONTENT_LENGTH")


class HeaderSet(OrderedDict):  # pragma: nocover
    def __init__(self, items=None):
        super().__init__()
        for i in items or []:
            self.add(i)

    def add(self, k, *args):
        if isinstance(k, str):
            values = []
            if ":" in k:
                k, v = k.split(":", 1)
                values += [i.strip() for i in v.split(";")]

        else:
            k, v = k
            values = [v]

        if args:
            values += args

        self[k] = "; ".join(values)

    def __getitem__(self, k):
        return super().__getitem__(k.lower())

    def __setitem__(self, k, v):
        return super().__setitem__(k.lower(), v)

    def __delitem__(self, k):
        return super().__delitem__(k)

    def __iter__(self):
        for k, v in self.items():
            yield f"{k}: {v}"

    def __str__(self):
        return "\r\n".join(self)

    def __iadd__(self, other):
        for i in other:
            self.add(i)

        return self

    def load_from_wsgi_environ(self, environ):
        for key, value in environ.items():
            if key.startswith("HTTP_") and key not in content_environ:
                header_name = key[5:].replace("_", "-")
                self[header_name] = value

            elif key in content_headers and value:
                header_name = key.replace("_", "-")
                self[header_name] = value

        return self

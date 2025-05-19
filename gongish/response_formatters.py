try:
    import ujson as jsonlib

    def dump_json(v, indent):  # pragma: nocover
        # ujson 4.x patch
        # https://github.com/ultrajson/ultrajson/issues/317
        if indent is None:
            indent = 0
        return jsonlib.dumps(v, indent=indent)

except ImportError:  # pragma: no cover
    import json as jsonlib

    dump_json = jsonlib.dumps


class ResponseFormattersMixin:
    @staticmethod
    def format_text(request, response):
        response.type = "text/plain"
        response.charset = "utf-8"

    @staticmethod
    def format_html(request, response):
        response.type = "text/html"
        response.charset = "utf-8"

    @staticmethod
    def format_xml(request, response):
        response.type = "application/xml"
        response.charset = "utf-8"

    @staticmethod
    def format_json(request, response, indent=None):
        response.type = "application/json"
        response.charset = "utf-8"
        response.body = dump_json(response.body, indent=indent)

    @staticmethod
    def format_binary(request, response):
        response.type = "application/octet-stream"

    default_formatter = format_text

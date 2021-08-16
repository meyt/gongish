try:
    import ujson as jsonlib

    def dump_json(v, indent):
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
        # Format in plain text
        response.type = "text/plain"
        response.charset = "utf-8"

    @staticmethod
    def format_json(request, response, indent=None):
        # Format in JSON
        response.type = "application/json"
        response.charset = "utf-8"
        response.body = dump_json(response.body, indent=indent)

    @staticmethod
    def format_binary(request, response):
        # Format in Binary
        response.type = "application/octet-stream"

    __default_formatter__ = format_text

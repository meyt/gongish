try:
    import ujson as jsonlib
except ImportError:  # pragma: no cover
    import json as jsonlib


class ResponseFormattersMixin:
    @staticmethod
    def format_text(request, response):
        # Format in plain text
        response.type = "text/plain"
        response.charset = "utf-8"
        response.body = str(response.body)

    @staticmethod
    def format_json(request, response, indent=None):
        # Format in JSON
        response.type = "application/json"
        response.charset = "utf-8"
        response.body = jsonlib.dumps(response.body, indent=indent)

    @staticmethod
    def format_binary(request, response):
        # Format in Binary
        response.type = "application/octet-stream"

    __default_formatter__ = format_text

import logging
from contextvars import ContextVar

from gongish.configuration import ConfigurationMixin
from gongish.router import RouterMixin


class Application(RouterMixin, ConfigurationMixin):
    _log = logging.getLogger("gongish")
    _current_app_var = ContextVar("current_app", default=None)

    def __init__(self):
        ConfigurationMixin.__init__(self)
        RouterMixin.__init__(self)

    def setup(self):  # pragma: nocover
        pass

    def shutdown(self):  # pragma: nocover
        pass


def current_app():
    return Application._current_app_var.get()

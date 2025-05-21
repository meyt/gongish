import logging
import threading

from gongish.configuration import ConfigurationMixin
from gongish.router import RouterMixin


class Application(RouterMixin, ConfigurationMixin):
    _log = logging.getLogger("gongish")
    _thread_local = threading.local()

    def __init__(self):
        self.__class__._thread_local.current_app = self
        ConfigurationMixin.__init__(self)
        RouterMixin.__init__(self)

    def setup(self):  # pragma: nocover
        self.__class__._thread_local.current_app = self

    def shutdown(self):  # pragma: nocover
        self.__class__._thread_local.current_app = None


def get_current_app():
    if not hasattr(Application._thread_local, "current_app"):
        return

    return Application._thread_local.current_app

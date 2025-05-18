import logging
import threading

from gongish.configuration import ConfigurationMixin
from gongish.router import RouterMixin


class Application(RouterMixin, ConfigurationMixin):
    _log = logging.getLogger("gongish")
    _thread_local = threading.local()

    def __init__(self):
        ConfigurationMixin.__init__(self)
        RouterMixin.__init__(self)

    def setup(self):  # pragma: nocover
        raise NotImplementedError

    def shutdown(self):  # pragma: nocover
        raise NotImplementedError

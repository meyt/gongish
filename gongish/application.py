import logging

from gongish.router import RouterMixin
from gongish.configuration import ConfigurationMixin


logger = logging.getLogger("gongish")


class Application(RouterMixin, ConfigurationMixin):

    #: Application logger based on python builtin logging module
    __logger__ = logger

    def __init__(self):
        ConfigurationMixin.__init__(self)
        RouterMixin.__init__(self)

    def setup(self):  # pragma: nocover
        raise NotImplementedError

    def shutdown(self):  # pragma: nocover
        raise NotImplementedError

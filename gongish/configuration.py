import os

from pymlconf import Root
from gongish import __version__


class ConfigurationMixin:
    def __init__(self):
        context = {"version": __version__}
        context.update(os.environ)
        data = {"debug": True}
        self.config = Root(data=data, context=context)

    def configure(self, filename: str):
        self.config.loadfile(filename)

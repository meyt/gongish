import os

from pymlconf import Root


class ConfigurationMixin:
    def __init__(self):
        from gongish import __version__

        context = {"gongish_version": __version__}
        context.update(os.environ)
        data = {"debug": True}
        self.config = Root(data=data, context=context)

    def configure(self, filename: str):
        self.config.loadfile(filename)

import os

from os.path import isdir, join, relpath, pardir, exists
from time import strftime, gmtime
from mimetypes import guess_type
from .exceptions import HTTPNotFound, HTTPForbidden
from .constants import HTTP_DATETIME_FORMAT


class StaticHandlerMixin:
    def add_static(
        self,
        path: str,
        directory: str,
        default_document: str = "index.html",
        chunk_size: int = 0x4000,
    ):
        def get(*remaining_paths):
            response = self.response
            # response.charset = "utf-8"

            # Find the physical path of the given path parts
            physical_path = join(directory, *remaining_paths)

            # Check to do not access the parent directory of root and also we
            # are not listing directories here.
            if pardir in relpath(physical_path, directory):
                raise HTTPForbidden

            if isdir(physical_path):
                physical_path = join(physical_path, default_document)
                if not (default_document and exists(physical_path)):
                    raise HTTPNotFound()

            response.headers["content-type"] = (
                guess_type(physical_path)[0] or "application/octet-stream"
            )

            try:
                f = open(physical_path, mode="rb")
                stat = os.fstat(f.fileno())
                response.headers["content-length"] = str(stat[6])
                response.headers["last-modified"] = strftime(
                    HTTP_DATETIME_FORMAT, gmtime(stat.st_mtime)
                )

                with f:
                    while True:
                        r = f.read(chunk_size)
                        if not r:
                            break
                        yield r

            except OSError:
                raise HTTPNotFound

        self.route(path=path, formatter=lambda x, y: None)(get)
        self.route(path=f"{path}/*", formatter=lambda x, y: None)(get)

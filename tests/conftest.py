import pytest

from os.path import join, dirname

_this_dir = dirname(__file__)
_stuff_dir = join(_this_dir, "stuff")


@pytest.fixture
def stuff_dir():
    return _stuff_dir

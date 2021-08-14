import sys

from . import serve


def main():
    if len(sys.argv) > 0 and sys.argv[1] == "serve":
        return serve.main(sys.argv[2:])

    print("\n".join(("Gongish CLI", "", "Commands:", "gongish serve")))

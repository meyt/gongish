import importlib
from argparse import ArgumentParser
from wsgiref.simple_server import make_server


p = ArgumentParser(
    prog="gongish serve", description="Serve a WSGI application"
)
p.add_argument(
    "module",
    nargs="?",
    help="Module and application name (e.g: myapp:app)",
    type=str,
)
p.add_argument(
    "-b",
    "--bind",
    type=str,
    help="Bind address (default: localhost:8080)",
    default="localhost:8080",
)


def main(args):
    args = p.parse_args(args)
    module_name, module_attr = args.module.split(":")
    module = importlib.import_module(module_name)
    app = getattr(module, module_attr)

    bind = args.bind
    if bind.startswith(":"):
        host = "localhost"
        port = bind[1:]
    elif ":" in bind:
        host, port = bind.split(":")
    else:
        host = bind
        port = "8080"

    httpd = make_server(host, int(port), app)
    print(f"Serving http://{host}:{port}")
    httpd.serve_forever()

import pytest
import webtest

from gongish import Application


def test_default_formatter():
    class MyApp(Application):
        default_formatter = Application.format_json

    app = MyApp()

    @app.route("/")
    def get():
        return dict(a=1)

    @app.route("/none")
    def get():
        return

    @app.route("/int")
    def get():
        return 12

    @app.route("/str")
    def get():
        return "thestr"

    testapp = webtest.TestApp(app)

    resp = testapp.get("/")
    assert resp.json == dict(a=1)
    assert resp.status == "200 OK"

    resp = testapp.get("/none")
    assert resp.json is None

    resp = testapp.get("/int")
    assert resp.json == 12

    resp = testapp.get("/str")
    assert resp.json == "thestr"


def test_text_formatters():
    class MyApp(Application):
        default_formatter = Application.format_text

    app = MyApp()

    @app.route("/")
    def get():
        return "thestring"

    @app.route("/nonstr")
    def get():
        return 12

    @app.route("/none")
    def get():
        return

    @app.text("/decorator")
    def get():
        return

    @app.html("/html")
    def get():
        return "<html><body><h1>Hi!</h1></body></html>"

    @app.xml("/xml")
    def get():
        return "<svg></svg>"

    testapp = webtest.TestApp(app)

    resp = testapp.get("/")
    assert resp.body == b"thestring"

    resp = testapp.get("/none")
    assert resp.body == b""

    testapp.get("/nonstr", status=500)
    resp = testapp.get("/decorator")
    assert resp.headers["content-type"] == "text/plain; charset=utf-8"
    assert resp.body == b""

    resp = testapp.get("/html")
    assert resp.headers["content-type"] == "text/html; charset=utf-8"
    assert resp.body == b"<html><body><h1>Hi!</h1></body></html>"

    resp = testapp.get("/xml")
    assert resp.headers["content-type"] == "application/xml; charset=utf-8"
    assert resp.body == b"<svg></svg>"


def test_unknown_formatter():
    class MyApp(Application):
        default_formatter = Application.format_text

    app = MyApp()

    @app.route("/")
    def get():
        return "index"

    with pytest.raises(AttributeError) as e:

        @app.unknown("/unknown")
        def get():
            return "pass"

    assert (
        str(e.value)
        == "'MyApp' object has no attribute 'format_unknown' or 'unknown'"
    )

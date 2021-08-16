import webtest

from gongish import Application


def test_default_formatter():
    class MyApp(Application):
        __default_formatter__ = Application.format_json

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
        return 'thestr'

    testapp = webtest.TestApp(app)

    resp = testapp.get("/")
    assert resp.json == dict(a=1)
    assert resp.status == "200 OK"

    resp = testapp.get("/none")
    assert resp.json is None

    resp = testapp.get("/int")
    assert resp.json == 12

    resp = testapp.get("/str")
    assert resp.json == 'thestr'


def test_text_formatter():
    class MyApp(Application):
        __default_formatter__ = Application.format_text

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

    testapp = webtest.TestApp(app)

    resp = testapp.get("/")
    assert resp.body == b"thestring"

    resp = testapp.get("/none")
    assert resp.body == b""

    testapp.get("/nonstr", status=500)

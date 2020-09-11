import webtest

from gongish import Application


def test_default_formatter():
    class MyApp(Application):
        __default_formatter__ = Application.format_json

    app = MyApp()

    @app.route("/")
    def get():
        return dict(a=1)

    testapp = webtest.TestApp(app)
    resp = testapp.get("/")
    assert resp.json == dict(a=1)
    assert resp.status == "200 OK"

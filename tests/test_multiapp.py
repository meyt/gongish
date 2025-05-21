import webtest

from gongish import Application, current_app


def test_multiapp():
    assert current_app() is None

    app1 = Application()

    @app1.route("/")
    def get():
        assert current_app() is app1
        return "The Root"

    testapp1 = webtest.TestApp(app1)
    resp = testapp1.get("/")
    assert resp.text == "The Root"
    assert resp.status == "200 OK"
    assert app1.request is None
    assert current_app() is None

    app2 = Application()

    @app2.route("/")
    def get():
        assert current_app() is app2
        return "The Root"

    assert app2.request is None
    assert current_app() is None

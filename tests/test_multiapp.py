import webtest

from gongish import Application


def test_multiapp():
    app1 = Application()

    @app1.route("/")
    def get():
        return "The Root"

    testapp1 = webtest.TestApp(app1)
    resp = testapp1.get("/")
    assert resp.text == "The Root"
    assert resp.status == "200 OK"
    assert app1.request is None

    app2 = Application()

    @app2.route("/")
    def get():
        return "The Root"

    assert app2.request is None

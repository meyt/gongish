import pytest
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

    with pytest.raises(AttributeError) as e:
        assert app1.request
    assert str(e.value) == "'_thread._local' object has no attribute 'request'"

    app2 = Application()

    @app2.route("/")
    def get():
        return "The Root"

    with pytest.raises(AttributeError) as e:
        assert app2.request

    assert str(e.value) == "'_thread._local' object has no attribute 'request'"

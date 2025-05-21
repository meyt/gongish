from http import cookies

import webtest

from gongish import Application


def test_simple_route():

    app = Application()

    @app.text("/cookies")
    def get():
        cookies = app.request.cookies
        counter = cookies["counter"]
        cookies["counter"] = str(int(counter.value) + 1)
        cookies["counter"]["max-age"] = 1
        cookies["counter"]["path"] = "/a"
        cookies["counter"]["domain"] = "example.com"
        return "Cookies"

    testapp = webtest.TestApp(app)

    resp = testapp.get("/cookies", headers={"cookie": "counter=1;"})
    assert resp.text == "Cookies"
    assert "Set-cookie" in resp.headers

    cookie = cookies.SimpleCookie(resp.headers["Set-cookie"])
    counter = cookie["counter"]
    assert counter.value == "2"
    assert counter["path"] == "/a"
    assert counter["domain"] == "example.com"
    assert counter["max-age"] == "1"

    app.shutdown()

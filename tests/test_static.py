from os.path import join
from webtest import TestApp
from gongish import Application


def test_static(stuff_dir):
    app = Application()
    app.add_static("/public", stuff_dir)
    app.add_static("/lost", join(stuff_dir, "lost"))

    @app.route("/")
    def get():
        return "The Root"

    testapp = TestApp(app)

    resp = testapp.get("/")
    assert resp.text == "The Root"
    assert resp.status == "200 OK"

    resp = testapp.get("/public")
    assert resp.text == "<h1>Hi!</h1>"
    assert resp.headers["content-type"] == "text/html"
    assert resp.status == "200 OK"

    resp = testapp.get("/public/index.html")
    assert resp.text == "<h1>Hi!</h1>"
    assert resp.headers["content-type"] == "text/html"
    assert resp.headers["last-modified"] == "Fri, 13 Aug 2021 14:16:44 GMT"

    resp = testapp.get("/public/img1.png")
    assert len(resp.body) == 72332
    assert resp.headers["content-type"] == "image/png"
    assert resp.headers["last-modified"] == "Sun, 02 Feb 2020 04:51:41 GMT"

    testapp.get("/lost", status=404)
    testapp.get("/public/img1.jpg", status=404)
    testapp.get("/public/subdir", status=404)
    testapp.get("/public/../conftest.py", status=403)
    testapp.get("/public/../../setup.py", status=403)

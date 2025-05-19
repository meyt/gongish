import os
from os.path import join

import webtest

from gongish import Application


def test_static(stuff_dir):
    app = Application()
    app.add_static("/public", stuff_dir)
    app.add_static("/lost", join(stuff_dir, "lost"))

    os.utime(join(stuff_dir, "index.html"), (1602179630, 1602179635))
    os.utime(join(stuff_dir, "img1.png"), (1602179640, 1602179645))

    @app.route("/")
    def get():
        return "The Root"

    testapp = webtest.TestApp(app)

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
    assert resp.headers["last-modified"] == "Thu, 08 Oct 2020 17:53:55 GMT"

    resp = testapp.get("/public/img1.png")
    assert len(resp.body) == 72332
    assert resp.headers["content-type"] == "image/png"
    assert resp.headers["last-modified"] == "Thu, 08 Oct 2020 17:54:05 GMT"

    resp = testapp.get("/public/static-subdir/fake-index.html")
    assert resp.headers["content-type"] == "text/html"
    assert resp.text == "<h1>Hello from subdir!</h1>"

    testapp.get("/lost", status=404)
    testapp.get("/public/img1.jpg", status=404)
    testapp.get("/public/subdir", status=404)
    testapp.get("/public/static-subdir", status=404)
    testapp.get("/public/../conftest.py", status=403)
    testapp.get("/public/../../setup.py", status=403)

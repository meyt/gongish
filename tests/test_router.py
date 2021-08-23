import pytest
import webtest

from gongish import Application
from gongish.request import Request


def test_simple_route():

    app = Application()

    @app.route("/")
    def get():
        return "The Root"

    @app.route("/user")
    def GET():
        return "User Route"

    @app.route("/user")
    def POST():
        return "User Route Post"

    @app.route("/user/:userid")
    def delete(userid: int):
        return f"Delete User {userid}"

    @app.route("/user/email/:email/book")
    def get(email: str):
        return f"Get user {email} books"

    @app.route("/user/:userid/book")
    def get(userid: str):
        return f"Get user {userid} books"

    @app.route("/user/:userid/book/year/:year")
    def get(userid: str, year: int):
        return f"Get user {userid} books for year {year}"

    @app.json("/request")
    def get():
        return {
            "fullpath": app.request.fullpath,
            "contenttype": app.request.contenttype,
            "query": app.request.query,
            "cookies": app.request.cookies,
            "scheme": app.request.scheme,
            "response_type": app.response.type,
            "response_charset": app.response.charset,
        }

    @app.binary("/binary")
    def get():
        return b"TheMachine!"

    @app.text("/no_annotation/:name")
    def get(name):
        return name

    @app.json("/wildcard1/*")
    def get(*args):
        return args

    @app.json("/wildcard1/*")
    def post(*args):
        return args

    @app.json("/wildcard1/wildcardinner/*")
    def get(*args):
        return args

    @app.json("/wildcard2/wildcardinner/*")
    def get(*args):
        return args

    testapp = webtest.TestApp(app)
    resp = testapp.get("/")
    assert resp.text == "The Root"
    assert resp.status == "200 OK"

    resp = testapp.get("/user")
    assert resp.text == "User Route"
    assert resp.status == "200 OK"

    resp = testapp.post("/user")
    assert resp.text == "User Route Post"
    assert resp.status == "200 OK"

    resp = testapp.delete("/user/4")
    assert resp.text == "Delete User 4"
    assert resp.status == "200 OK"

    resp = testapp.get("/user/email/x@site.com/book")
    assert resp.text == "Get user x@site.com books"
    assert resp.status == "200 OK"

    resp = testapp.get("/user/5/book/year/2001")
    assert resp.text == "Get user 5 books for year 2001"
    assert resp.status == "200 OK"

    resp = testapp.get("/request")
    assert resp.json == {
        "fullpath": "http://localhost:80/request",
        "contenttype": None,
        "query": {},
        "cookies": {},
        "scheme": "http",
        "response_type": None,
        "response_charset": None,
    }

    resp = testapp.get("/binary")
    assert resp.body == b"TheMachine!"

    resp = testapp.get("/no_annotation/john")
    assert resp.text == "john"

    resp = testapp.get("/wildcard1/first")
    assert resp.json == ["first"]

    resp = testapp.get("/wildcard2/wildcardinner/first")
    assert resp.json == ["first"]

    resp = testapp.get("/wildcard1/wildcardinner/a/b/c/d/e/f/g/h")
    assert resp.json == "a/b/c/d/e/f/g/h".split("/")

    resp = testapp.get("/wildcard2/wildcardinner/a/b/c/d/e/f/g/h")
    assert resp.json == "a/b/c/d/e/f/g/h".split("/")

    resp = testapp.get("/wildcard1/a/b/c/d/e/f/g/h")
    assert resp.json == "a/b/c/d/e/f/g/h".split("/")

    resp = testapp.post_json("/wildcard1/first")
    assert resp.json == ["first"]

    resp = testapp.post_json("/wildcard1/a/b/c/d/e/f/g/h")
    assert resp.json == "a/b/c/d/e/f/g/h".split("/")

    # Query string not existed
    assert Request({"REQUEST_METHOD": "GET"}).query == {}


def test_content_type():
    app = Application()
    testapp = webtest.TestApp(app)

    @app.route("/")
    def get():
        return "The Root"

    @app.text("/user")
    def get():
        return "The User"

    @app.json("/user")
    def post():
        return dict(id="bla")

    resp = testapp.get("/")
    assert resp.text == "The Root"
    assert resp.headers["content-type"] == "text/plain; charset=utf-8"

    resp = testapp.get("/user")
    assert resp.text == "The User"
    assert resp.headers["content-type"] == "text/plain; charset=utf-8"

    resp = testapp.post("/user")
    assert resp.json == dict(id="bla")
    assert resp.headers["content-type"] == "application/json; charset=utf-8"


def test_stream():
    app = Application()
    testapp = webtest.TestApp(app)

    @app.route("/")
    def get():
        yield "Foo"
        yield "Bar"

    @app.route("/haslength")
    def get():
        app.response.length = 6
        yield "Foo"
        yield "Bar"

    @app.binary("/binary")
    def get():
        yield b"Foo"
        yield b"Bar"

    @app.route("/bad")
    def get():
        yield "Foo"
        raise ValueError("something wrong")

    @app.route("/chunked")
    @app.chunked
    def get():
        yield "first"
        yield "second"

    @app.route("/chunked_trailer")
    @app.chunked("trailer1", "end")
    def get():
        yield "first"
        yield "second"

    @app.route("/bad_chunked")
    @app.chunked
    def get():
        yield "first"
        raise Exception("error in streaming")

    resp = testapp.get("/")
    assert resp.text == "FooBar"
    assert resp.headers["content-type"] == "text/plain; charset=utf-8"

    resp = testapp.get("/haslength")
    assert resp.text == "FooBar"
    assert resp.headers["content-type"] == "text/plain; charset=utf-8"
    assert resp.headers["content-length"] == "6"

    resp = testapp.get("/binary")
    assert resp.body == b"FooBar"
    assert resp.headers["content-type"] == "application/octet-stream"

    # Headers already sent and cannot handle exception in HTTP
    with pytest.raises(ValueError):
        testapp.get("/bad")

    resp = testapp.get("/chunked")
    assert resp.headers["transfer-encoding"] == "chunked"
    assert "trailer" not in resp.headers
    assert resp.text == "5\r\nfirst\r\n6\r\nsecond\r\n0\r\n\r\n"

    resp = testapp.get("/chunked_trailer")
    assert resp.headers["transfer-encoding"] == "chunked"
    assert resp.headers["trailer"] == "trailer1"
    assert (
        resp.text == "5\r\nfirst\r\n6\r\nsecond\r\n0\r\ntrailer1: end\r\n\r\n"
    )

    resp = testapp.get("/bad_chunked")
    assert resp.headers["transfer-encoding"] == "chunked"
    assert "trailer" not in resp.headers
    assert resp.text == "5\r\nfirst\r\n18\r\nerror in streaming0\r\n\r\n"

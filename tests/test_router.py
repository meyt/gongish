import webtest

from gongish import Application
from gongish.request import Request


def test_simple_route():

    app = Application()

    @app.route("/")
    def get():
        return "The Root"

    @app.route("/user")
    def get():
        return "User Route"

    @app.route("/user")
    def post():
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

    # Query string not existed
    assert Request({"REQUEST_METHOD": "GET"}).query == {}

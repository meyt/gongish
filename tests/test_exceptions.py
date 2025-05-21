import webtest

from gongish import (
    Application,
    HTTPFound,
    HTTPInternalServerError,
    HTTPKnownStatus,
    HTTPMovedPermanently,
    HTTPNoContent,
    HTTPNotFound,
)


def test_http_status():

    app = Application()

    @app.route("/no_content")
    def get():
        app.response.headers["custom-one"] = "yes"
        raise HTTPNoContent

    @app.route("/old_page")
    def get():
        raise HTTPFound("https://localhost/new_page")

    @app.route("/old_user")
    def get():  # noqa: F811
        raise HTTPMovedPermanently("https://localhost/new_user")

    @app.route("/oops")
    def get():
        app.response.headers["custom-one"] = "false"
        return 12 / 0

    testapp = webtest.TestApp(app)

    resp = testapp.get("/no_content", status=HTTPNoContent.code)
    assert resp.headers["custom-one"] == "yes"
    assert "content-type" not in resp.headers

    resp = testapp.get("/old_page", status=HTTPFound.code)
    assert resp.headers["location"] == "https://localhost/new_page"
    assert "content-type" not in resp.headers

    resp = testapp.get("/old_user", status=HTTPMovedPermanently.code)
    assert resp.headers["location"] == "https://localhost/new_user"
    assert "content-type" not in resp.headers

    resp = testapp.get("/oops", status=HTTPInternalServerError.code)
    assert resp.status == HTTPInternalServerError().status
    assert resp.headers["content-type"] == "text/plain; charset=utf-8"
    assert "custom-one" not in resp.headers

    # Custom exception
    class InvalidEmail(HTTPKnownStatus):
        code, text = (700, "Invalid Email")

    @app.route("/user")
    def post():
        raise InvalidEmail

    resp = testapp.post("/user", status=InvalidEmail.code)
    assert resp.status == "700 Invalid Email"

    app.shutdown()


def test_exception_on_production():
    app = Application()
    app.config.debug = False

    @app.route("/")
    def get():
        raise HTTPNotFound("im not here")

    @app.route("/empty")
    def get():
        raise HTTPNoContent("im empty")

    testapp = webtest.TestApp(app)

    resp = testapp.get("/", status=HTTPNotFound.code)
    assert resp.status == "404 im not here"
    assert resp.body == b"404 im not here"

    resp = testapp.get("/empty", status=HTTPNoContent.code)
    assert resp.status == "204 im empty"
    assert resp.body == b""
    assert "content-type" not in resp.headers

    app.config.debug = True

    resp = testapp.get("/", status=HTTPNotFound.code)
    assert resp.status == "404 im not here"
    assert resp.body.decode().startswith("Traceback (")

    resp = testapp.get("/empty", status=HTTPNoContent.code)
    assert resp.status == "204 im empty"
    assert resp.body == b""
    assert "content-type" not in resp.headers

    app.shutdown()

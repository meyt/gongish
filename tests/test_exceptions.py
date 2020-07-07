import webtest

from gongish import (
    Application,
    HTTPKnownStatus,
    HTTPFound,
    HTTPMovedPermanently,
    HTTPNoContent,
    HTTPInternalServerError,
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

    resp = testapp.get("/old_page", status=HTTPFound.code)
    assert resp.headers["location"] == "https://localhost/new_page"

    resp = testapp.get("/old_user", status=HTTPMovedPermanently.code)
    assert resp.headers["location"] == "https://localhost/new_user"

    resp = testapp.get("/oops", status=HTTPInternalServerError.code)
    assert resp.status == HTTPInternalServerError().status
    assert "custom-one" not in resp.headers

    # Custom exception
    class InvalidEmail(HTTPKnownStatus):
        code, text = (700, "Invalid Email")

    @app.route("/user")
    def post():
        raise InvalidEmail

    resp = testapp.post("/user", status=InvalidEmail.code)
    assert resp.status == "700 Invalid Email"

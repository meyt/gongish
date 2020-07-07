import pytest
import webtest

from gongish import Application, HTTPBadRequest
from gongish.request import RequestForm


def test_forms():

    app = Application()

    @app.json("/user")
    def post():
        return {"headers": dict(app.request.headers), "form": app.request.form}

    @app.json("/user/avatar")
    def put():
        return {
            "headers": dict(app.request.headers),
            "avatar": app.request.form.avatar.filename,
        }

    testapp = webtest.TestApp(app)

    # URL Encoded form data
    resp = testapp.post("/user", params={"firstname": "John", "age": 18})
    assert (
        resp.json["headers"]["content-type"]
        == "application/x-www-form-urlencoded"
    )
    assert resp.json["form"] == {"firstname": "John", "age": "18"}

    # JSON form data
    resp = testapp.post_json("/user", params={"firstname": "John", "age": 18})
    assert resp.json["headers"]["content-type"] == "application/json"
    assert resp.json["form"] == {"firstname": "John", "age": 18}

    # Multipart form data
    resp = testapp.put(
        "/user/avatar", upload_files=[("avatar", "avatar.png", b"BlaBla!")]
    )
    assert resp.json["headers"]["content-type"].startswith(
        "multipart/form-data"
    )
    assert resp.json["avatar"] == "avatar.png"

    # Bad wsgi.input
    with pytest.raises(HTTPBadRequest):
        RequestForm(
            {"REQUEST_METHOD": "POST", "wsgi.input": []},
            "multipart/form-data",
            0,
        )

    # No content-length
    with pytest.raises(HTTPBadRequest):
        RequestForm(
            {"REQUEST_METHOD": "GET", "wsgi.input": ""},
            "application/json",
            None,
        )

    # Invalid JSON
    with pytest.raises(HTTPBadRequest):
        RequestForm(
            {"REQUEST_METHOD": "GET", "wsgi.input": b"{"},
            "application/json",
            0,
        )

    # Absent query string
    RequestForm(
        {"REQUEST_METHOD": "GET", "wsgi.input": ""},
        "application/x-www-form-urlencoded",
        0,
    )

    # Array field
    assert RequestForm(
        {
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "foo=bar&foo=baz",
            "wsgi.input": "",
        },
        "application/x-www-form-urlencoded",
        0,
    ).foo == ["bar", "baz"]

    # Form attribute existence
    assert (
        RequestForm(
            {
                "REQUEST_METHOD": "GET",
                "QUERY_STRING": "foo=bar&foo=baz",
                "wsgi.input": "",
            },
            "application/x-www-form-urlencoded",
            0,
        ).bar
        is None
    )

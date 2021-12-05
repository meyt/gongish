import pytest
import webtest

from datetime import datetime, date, time

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
    assert (
        RequestForm(
            {
                "REQUEST_METHOD": "GET",
                "QUERY_STRING": "foo=bar&foo=baz",
                "wsgi.input": "",
            },
            "application/x-www-form-urlencoded",
            0,
        ).foo
        == ["bar", "baz"]
    )

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


def make_form(v, is_json=False):
    import io
    import os
    import json
    import urllib.parse

    def get_streamlength(s):

        s.seek(0, os.SEEK_END)
        res = s.tell()
        s.seek(0)
        return res

    if is_json:
        fp = io.StringIO("")
        v = {"a": v}
        v = json.dump(v, fp)
        clength = get_streamlength(fp)
        environ = {
            "REQUEST_METHOD": "POST",
            "wsgi.input": fp,
        }
        ctype = "application/json"

    else:
        ctype = "application/x-www-form-urlencoded"
        clength = None
        environ = {
            "REQUEST_METHOD": "GET",
            "wsgi.input": "",
        }
        if v is not None:
            environ["QUERY_STRING"] = f"a={urllib.parse.quote_plus(v)}"

    return RequestForm(environ, ctype, clength)


def test_date_format():
    form = make_form("2001-01-01")
    assert form.get_date("a") == date(2001, 1, 1)

    # check default
    form = make_form(None)
    assert form.get_date("a", None) is None

    form = make_form(None)
    assert form.get_date("a", "2001-01-01") == date(2001, 1, 1)

    form = make_form(None)
    assert form.get_date("a", date(2001, 1, 1)) == date(2001, 1, 1)

    # iso date format
    with pytest.raises(HTTPBadRequest, match=r"Invalid date format.*"):
        make_form("01-01-01").get_date("a")

    # none iso date format
    with pytest.raises(HTTPBadRequest, match=r"Invalid date format.*"):
        make_form("2001/01/01").get_date("a")


def test_time_format():
    form = make_form("08:08:08")
    assert form.get_time("a") == time(8, 8, 8)

    # check default
    form = make_form(None)
    assert form.get_time("a", None) is None

    form = make_form(None)
    assert form.get_time("a", "08:08:08") == time(8, 8, 8)

    form = make_form(None)
    assert form.get_time("a", time(8, 8, 8)) == time(8, 8, 8)

    # none iso time format
    with pytest.raises(HTTPBadRequest, match=r"Invalid time format.*"):
        make_form("08-08-08").get_time("a")


def test_datetime_format():
    form = make_form("2017-10-10T10:10:00")
    assert form.get_datetime("a") == datetime(2017, 10, 10, 10, 10, 0)

    form = make_form("2017-10-10T10:10:00.")
    assert form.get_datetime("a") == datetime(2017, 10, 10, 10, 10, 0)

    # check default
    form = make_form(None)
    assert form.get_datetime("a", None) is None

    form = make_form(None)
    assert form.get_datetime("a", "2017-10-10T10:10:00") == datetime(
        2017, 10, 10, 10, 10, 0
    )

    form = make_form(None)
    assert form.get_datetime(
        "a", datetime(2017, 10, 10, 10, 10, 0)
    ) == datetime(2017, 10, 10, 10, 10, 0)

    # Invalid month value
    with pytest.raises(HTTPBadRequest, match=r"Invalid datetime format.*"):
        make_form("2017-13-10T10:10:00").get_datetime("a")

    # Invalid datetime format
    with pytest.raises(HTTPBadRequest, match=r"Invalid datetime format.*"):
        make_form("InvalidDatetime").get_datetime("a")

    # Empty datetime
    with pytest.raises(HTTPBadRequest, match=r"Invalid datetime format.*"):
        make_form("").get_datetime("a")

    # datetime might not have ending Z
    form = make_form("2017-10-10T10:10:00.4546")
    assert form.get_datetime("a") == datetime(2017, 10, 10, 10, 10, 0, 4546)

    # datetime containing ending Z
    form = make_form("2017-10-10T10:10:00.4546Z")
    assert form.get_datetime("a") == datetime(2017, 10, 10, 10, 10, 0, 4546)

    # datetime with timezone
    form = make_form("2017-10-10T10:10:00.4546+03:00")
    assert form.get_datetime("a") == datetime(2017, 10, 10, 10, 10, 0, 4546)

    # datetime without microsecond
    form = make_form("2017-10-10T10:10:00+03:00")
    assert form.get_datetime("a") == datetime(2017, 10, 10, 10, 10, 0, 0)


def test_get_boolean():
    form = make_form(None, is_json=True)
    assert form.get_boolean("a") is None

    form = make_form(True, is_json=True)
    assert form.get_boolean("a") is True

    form = make_form("True", is_json=True)
    assert form.get_boolean("a") is True

    form = make_form("True", is_json=False)
    assert form.get_boolean("a") is True

    form = make_form("TruE", is_json=False)
    assert form.get_boolean("a") is True

    form = make_form("true", is_json=False)
    assert form.get_boolean("a") is True

    form = make_form(False, is_json=True)
    assert form.get_boolean("a") is False

    form = make_form("False", is_json=True)
    assert form.get_boolean("a") is False

    form = make_form("False", is_json=False)
    assert form.get_boolean("a") is False

    form = make_form("FalsE", is_json=False)
    assert form.get_boolean("a") is False

from gongish.helpers import HeaderSet


def test_headerset():

    headers = HeaderSet().load_from_wsgi_environ({})
    assert headers == {}

    headers = HeaderSet().load_from_wsgi_environ(
        {"HTTP_CONTENT_TYPE": "text/plain"}
    )
    assert headers == {}

    headers = HeaderSet().load_from_wsgi_environ(
        {"HTTP_CONTENT_LENGTH": "8"}
    )
    assert headers == {}

    headers = HeaderSet().load_from_wsgi_environ(
        {
            "HTTP_CONTENT_LENGTH": "8",
            "HTTP_CONTENT_TYPE": "text/plain"
        }
    )
    assert headers == {}

    headers = HeaderSet().load_from_wsgi_environ(
        {
            "HTTP_CONTENT_LENGTH": "8",
            "HTTP_CONTENT_TYPE": "text/plain"
        }
    )
    assert headers == {}

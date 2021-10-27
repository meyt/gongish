from gongish.helpers import WordRouter


def test_wordrouter():
    wt = WordRouter()
    wt.add("get/user", lambda: "all users")
    wt.add("get/user/me", lambda: "my profile")
    wt.add("get/user/:", lambda x: f"the user no {x}")
    wt.add("delete/user/:", lambda x: f"delete user {x}")
    wt.add("post/user", lambda: "new user")
    wt.add("get/user/email/:email/book", lambda x: f"get books {x}")
    wt.add("get/user/:userid/book", lambda x: f"get books {x}")
    wt.add(
        "get/user/:userid/book/year/:year", lambda x, y: f"get books {x},{y}"
    )
    wt.add("get/wildcard/*", lambda *x: f"wildcard {','.join(x)}")
    wt.add("get/wildcard/inner/*", lambda *x: f"wildcard inner {','.join(x)}")

    assert wt("get/user") == "all users"
    assert wt("get/user/me") == "my profile"
    assert wt("get/user/3121") == "the user no 3121"
    assert wt("delete/user/1313") == "delete user 1313"
    assert wt("post/user") == "new user"
    assert wt("get/user/email/x@site.com/book") == "get books x@site.com"
    assert wt("get/user/12/book") == "get books 12"
    assert wt("get/user/1/book/year/2020") == "get books 1,2020"
    assert wt("get/wildcard/a") == "wildcard a"
    assert wt("get/wildcard/a/b") == "wildcard a,b"
    assert wt("get/wildcard/inner/a") == "wildcard inner a"
    assert wt("get/wildcard/inner/a/b") == "wildcard inner a,b"

    assert wt("get/users") is None
    assert wt("get/user/email/x@site.com") is None
    assert wt("get/user/email/x@site.com") is None

    wt = WordRouter()
    wt.add("get/user", lambda: "all users")
    wt.add("delete/user/:", lambda x: f"delete user {x}")
    assert wt("get/user") == "all users"
    assert wt("get/user/1") is None
    assert wt("delete/user/1") == "delete user 1"

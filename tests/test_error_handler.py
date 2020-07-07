import webtest

from gongish import Application


def test_error_handler():

    app = Application()

    @app.route("/user")
    def get():
        return "User Route"

    @app.route("/user/:userid")
    def delete(userid: int):
        return f"Delete User {userid}"

    testapp = webtest.TestApp(app)
    resp = testapp.get("/", status=404)
    assert resp.status == "404 Not Found"

    resp = testapp.get("/user/wrongway", status=404)
    assert resp.status == "404 Not Found"

    resp = testapp.delete("/user/kebab", status=400)
    assert resp.status == "400 Invalid Parameter `userid`"

    # Custom error handler
    class AnotherApp(Application):
        def on_error(self, exc):
            import json
            import traceback
            response = self.response
            response.charset = "utf-8"
            response.type = "application/json"
            response.body = (
                json.dumps(dict(traceback=traceback.format_exc()))
                if self.config.debug
                else exc.text
            )

    app = AnotherApp()

    testapp = webtest.TestApp(app)
    resp = testapp.get("/", status=404)
    assert 'traceback' in resp.json.keys()
    assert resp.status == "404 Not Found"

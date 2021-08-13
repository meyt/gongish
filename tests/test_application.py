import webtest
import tempfile

from os.path import join
from gongish import Application


def test_hooks():
    class MyApp(Application):
        request_begin_counter = 0
        response_begin_counter = 0
        response_end_counter = 0
        on_error_counter = 0

        def on_begin_request(self):
            self.request_begin_counter += 1

        def on_begin_response(self):
            self.response.headers["authorization"] = "fake-one"
            self.response_begin_counter += 1

        def on_end_response(self):
            self.response_end_counter += 1

        def on_error(self, exc):
            self.on_error_counter += 1

    app = MyApp()

    @app.route("/tom")
    def get():
        return "Tom"

    @app.route("/streamed")
    def get():
        yield "First"
        yield "Second"

    @app.route("/onerror")
    def get():
        raise Exception

    testapp = webtest.TestApp(app)

    resp = testapp.get("/tom")
    assert resp.text == "Tom"
    assert resp.headers["authorization"] == "fake-one"
    assert app.request_begin_counter == 1
    assert app.response_begin_counter == 1
    assert app.response_end_counter == 1

    resp = testapp.get("/streamed")
    assert resp.text == "FirstSecond"
    assert app.request_begin_counter == 2
    assert app.response_begin_counter == 2
    assert app.response_end_counter == 2

    testapp.get("/onerror", status=500)
    assert app.on_error_counter == 1
    assert app.request_begin_counter == 3
    assert app.response_begin_counter == 2
    assert app.response_end_counter == 3


def test_configuration():
    app = Application()
    config = """
    debug: False

    site_url: http://localhost
    """
    tempdir = tempfile.gettempdir()
    config_filename = join(tempdir, "tempconfig.yaml")
    with open(config_filename, "w") as f:
        f.write(config)

    app.configure(config_filename)
    assert app.config.site_url == "http://localhost"

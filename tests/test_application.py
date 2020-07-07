import webtest
import tempfile

from os.path import join
from gongish import Application


def test_hooks():
    class MyApp(Application):
        def begin_response(self):
            self.response.headers["authorization"] = "fake-one"

        def end_response(self):
            self.response_ended = True

    app = MyApp()

    @app.route("/tom")
    def get():
        return "Tom"

    testapp = webtest.TestApp(app)

    resp = testapp.get("/tom")
    assert resp.text == "Tom"
    assert resp.headers["authorization"] == "fake-one"
    assert app.response_ended


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

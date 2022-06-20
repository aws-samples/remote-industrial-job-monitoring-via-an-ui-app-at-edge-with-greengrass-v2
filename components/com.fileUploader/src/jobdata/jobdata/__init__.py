# pylint: disable=C0114,E0602
import typing as t

from flask import Flask
from flask import render_template
from flask_cors import CORS

if t.TYPE_CHECKING:
    from flask.wrappers import Response

from jobdata import config as cfg

app: Flask = Flask(__name__, static_url_path="/", static_folder=cfg.DOCS_DIR)
#CORS(app, resources={r"/api/*": {"origins": "*"}})
CORS(app)

from jobdata.api import *
from jobdata.utils import *

try:
    from ._version import __version__
except ImportError:
    __version__ = "Unknown version"

__all__ = api.__all__ + utils.__all__  # type: ignore


@app.route("/docs")
@app.route("/<path:path>")
def serve_docs(path: str = "index.html") -> "Response":
    return app.send_static_file(path)

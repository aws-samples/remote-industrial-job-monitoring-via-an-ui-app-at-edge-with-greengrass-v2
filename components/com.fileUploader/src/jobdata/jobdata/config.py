"""Settings for the jobdata application."""

import os
import uuid
import socket

here = os.path.abspath(os.path.dirname(__file__))

DEBUG = True  # Only for development, else False

DOCS_DIR = f"{os.path.dirname(here)}/docs/_build/html"
LOGS_DIR = f"{os.path.dirname(here)}/logs"

SESSION = str(uuid.uuid4())

LOG = f"{LOGS_DIR}/{SESSION}.log"

ISO8601 = "%Y-%m-%dT%H:%M:%SZ"

#USERNAME = os.getlogin()
HOSTNAME = socket.gethostname()

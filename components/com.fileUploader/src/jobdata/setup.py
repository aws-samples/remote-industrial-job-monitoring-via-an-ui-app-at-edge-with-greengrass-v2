"""
jobdata Application setup.

This script will install the `jobdata` package in the python 3.6+
environment. Before proceeding, please ensure you have a virtual env
setup and running.
"""

try:
    import setuptools
except ImportError:
    raise RuntimeError(
        "Could not install package in the environment as setuptools is "
        "missing. Please create a new virtual environment before proceeding"
    )

import platform

#MIN_PYTHON_VERSION = ("3", "6")

#if platform.python_version_tuple() < MIN_PYTHON_VERSION:
#    raise SystemExit(
#        "Could not install jobdata in the environment. The jobdata "
#        "package requires python version 3.6+, you are using "
#        f"{platform.python_version()}")

if __name__ == "__main__":
    setuptools.setup()

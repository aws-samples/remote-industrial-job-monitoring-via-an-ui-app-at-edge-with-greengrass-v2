"""
Common utilities.

The module provides host of implementations which are helpful for the
proper execution of the code. However, the speciality of this module is
that most of the implementations are indepedent of the primary goal of
execution.

.. versionadded:: 1.0.0
"""

import functools
import os
import sys
import time
import types
import typing as t

import boto3

from jobdata import config as cfg
from jobdata.utils import getLogger

__all__ = ["measure", "initialize"]

logger = getLogger()


def _silence_warnings() -> None:
    """
    Suppress flask warnings.

    This is a bit of a hack to disable or rather suppress the warning
    messages displayed by the Flask and werkzeug server.

    .. seealso:

        [1] https://gist.github.com/jerblack/735b9953ba1ab6234abb43174210d356
        [2] https://stackoverflow.com/a/57989189/14316408

    .. versionadded:: 1.0.0
    """
    logger.info("Preparing environment to suppress warnings")
    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *x: None  # type: ignore
    os.environ["WERKZEUG_RUN_MAIN"] = "true"


def initialize(debug: bool) -> None:
    """
    Initialize runtime environment & database.

    This function performs quite a few things. It checks if the service
    is supposed to run in DEBUG mode or not and accordingly behaves in
    that way thus preparing and setting up a lot of things in the
    process.

    The primary setup this function configures is the runtime
    environment, development or production. If working in development
    mode, a test database is downloaded and configured.

    .. versionadded:: 1.0.0
    """
    logger.info(f"Searching for database in {cfg.here}/data/")
    if debug:
        if os.getenv("FLASK_ENV") != "development":
            logger.info(
                "No active environment variable set, setting up default "
                "variable: development"
            )
            os.environ["FLASK_ENV"] = "development"
        logger.info("Application mode: DEBUG")
    else:
        logger.info("Application mode: PRODUCTION")
    _silence_warnings()


def measure(fnc: types.FunctionType) -> t.Callable[..., types.FunctionType]:
    """
    Decorator to measure the duration of processing event.

    This decorator provides with the measure of how much time the
    underlying process takes to complete the task. This implementation
    is fairly simple. It calculates both times, function call time and
    the module call time. However, please note that the module call
    time will be displayed only if the difference between function call
    time and module call time is adequately large.

    :param fnc: Function type object to decorate.
    :return: Decorated function with the measured attributes.

    ..code-block:: python

        >>> import time
        >>>
        >>> @measure
        ... def fnc(a, b):
        ...     return a * b
        ...
        >>> fnc(2, 3)
        fnc: execution completed in 7.245 ms
        >>>
        >>> @measure
        ... def fnc(a, b):
        ...     time.sleep(2)
        ...     return a * b
        ...
        >>> fnc(2, 3)
        fnc: execution completed in 2.241 seconds

    .. versionadded:: 1.0.0
    """

    @functools.wraps(fnc)
    def inner(*args: t.Any, **kwargs: t.Any) -> types.FunctionType:
        fnc_start = time.time()
        result = fnc(*args, **kwargs)
        f_t = time.time() - fnc_start
        f_time = f"{f_t:.3f} seconds" if f_t > 2.0 else f"{f_t * 1000:.1f} ms"
        logger.info(f"{fnc.__qualname__}: execution completed in {f_time}")
        return result

    return inner

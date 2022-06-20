"""
Logging module to capture and control the output logs.

The module provides the necessary implementations for overriding the
standard logging capabilities provided by default. This is done by
monkey patching the objects from the :py:mod:`logging` and
:py:mod:`werkzeug` modules.

Our main goal is to make a unified logging system which logs the events
and messages from both :py:mod:`jobdata` and :py:mod:`werkzeug` modules.
This allows us to gather all the logs at one place and makes it easy to
maintain them. This module is also responsible for rendering colors on
the terminal when the conditions are met.

.. code-block:: python

    >>> logger = getLogger(__name__)
    >>> logger.info("hello hello")
    2021-09-18T10:59:47Z   INFO workspace...:23 : hello hello
    >>> logger.warn("I'll be back...")
    2021-09-18T10:59:48Z   WARN workspace...:24 : I'll be back...
    >>>

.. versionadded:: 1.0.0
"""
# pylint: disable=C0103,E1101,R0402,R0903,R0913,W0212,W0231,W0621,W0622

import logging
import logging.handlers as handlers
import os
import re
import sys
import types
import typing as t

from werkzeug.serving import WSGIRequestHandler
from werkzeug.serving import _log
from werkzeug.urls import uri_to_iri

from jobdata.config import ISO8601

__version__ = "2.2.0"
__author__ = "XAMES3 <akshaymestry@tensoriot.com>"

__all__ = [
    "ANSIRequestHandler",
    "Logger",
    "RotatingFileHandler",
    "StreamHandler",
    "basicConfig",
    "getLogger",
]

SysExcInfoType = t.Tuple[type, BaseException, t.Optional[types.TracebackType]]

LOG_FMT: str = (
    "%(gray)s%(asctime)s %(color)s%(levelname)5s%(reset)s "
    "%(gray)s%(stack)s:%(lineno)d%(reset)s : %(message)s"
)
# See https://stackoverflow.com/a/14693789/14316408 for the RegEx
# behind the ANSI escape sequence.
ANSI_ESCAPE_RE: str = r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
ANSI_HUES: t.Mapping[int, str] = {
    90: "\x1b[38;5;242m",
    60: "\x1b[38;5;128m",
    50: "\x1b[38;5;197m",
    40: "\x1b[38;5;204m",
    30: "\x1b[38;5;215m",
    20: "\x1b[38;5;41m",
    10: "\x1b[38;5;14m",
    00: "\x1b[0m",
}
ATTRS: t.Tuple[str, ...] = ("color", "gray", "reset")

logging._levelToName = {
    60: "TRACE",
    50: "FATAL",
    40: "ERROR",
    30: "WARN",
    20: "INFO",
    10: "DEBUG",
    00: "NOTSET",
}

esc = re.compile(ANSI_ESCAPE_RE)


class ANSIFormatter(logging.Formatter):
    """
    An ANSI color scheme formatter class.

    This class formats the ``record.pathname`` & ``record.exc_info``
    attributes to generate an uniform and clear log message. The class
    adds gray hues to the message's metadata and colorizes log levels.

    :param fmt: Log message format, defaults to None.
    :param datefmt: Log datetime format, defaults to None.

    .. code-block:: python

        >>> import logging
        >>>
        >>> logger = logging.getLogger(__name__)
        >>> formatter = ANSIFormatter(fmt=..., datefmt=...)
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
        >>> logger.setLevel(logging.INFO)
        >>> logger.addHandler(handler)

    .. seealso::

        :py:meth:`logging.Formatter.format()`
        :py:meth:`logging.Formatter.formatException()`

    .. versionadded:: 1.0.0
    """

    def __init__(
        self, fmt: t.Optional[str] = None, datefmt: t.Optional[str] = None
    ) -> None:
        """Initialize ANSI formatter."""
        if fmt is None:
            fmt = LOG_FMT
        if datefmt is None:
            datefmt = ISO8601
        self.fmt = fmt
        self.datefmt = datefmt

    @staticmethod
    def colorize(record: logging.LogRecord) -> None:
        """
        Add colors to the logging levels by manipulating log record.

        This implementation works on the edge as it makes changes to
        the record object in runtime. This has a potential drawback.
        This can create memory leaks, so in order to handle this, we
        check if the logging stream is a TTY interface or not. If we
        are sure that the stream is a TTY, we modify the object. This
        implementation thus prevents the record to hold un-readable
        ANSI characters while writing to a file.

        :param record: Instance of the logged event.
        """
        if getattr(record, "isatty", False):
            setattr(record, "color", ANSI_HUES[record.levelno])
            setattr(record, "gray", ANSI_HUES[90])
            setattr(record, "reset", ANSI_HUES[00])
        else:
            for attr in ATTRS:
                setattr(record, attr, "")

    @staticmethod
    def decolorize(record: logging.LogRecord) -> None:
        """
        Remove ``color`` and ``reset`` attributes from the log record.

        Think of this method as anti-activity of the
        :py:meth:`ANSIFormatter.colorize()` method. This will prevent
        the record from writing un-readable ANSI characters to a non-TTY
        interface.

        :param record: Instance of the logged event.
        """
        for attr in ATTRS:
            delattr(record, attr)

    @staticmethod
    def formatException(
        ei: t.Union[SysExcInfoType, t.Tuple[None, ...]]
    ) -> str:
        r"""
        Format exception information as text.

        This implementation does not work directly. The standard
        :py:class:`logging.Formatter` is required. The parent class
        creates an output string with ``\n`` which needs to be trimmed
        and this method does this well.

        :param ei: Information about the captured exception.
        :return: Formatted exception string.
        """
        fnc, lineno = "<module>", 0
        cls, msg, tbk = ei
        if tbk:
            fnc, lineno = tbk.tb_frame.f_code.co_name, tbk.tb_lineno
        fnc = "on" if fnc in ("<module>", "<lambda>") else f"in {fnc}() on"
        return f"{cls.__name__}: {msg} line {lineno}"  # type: ignore

    @staticmethod
    def stack(path: str, fnc: str) -> str:
        """
        Format path as stack.

        :param path: Pathname of the module which is logging the event.
        :param fnc: Callable instance which is logging the event.
        :return: Spring Boot like formatted path, well sort of.

        .. note::

            If called from a module, the base path of the module would
            be used else "shell" would be returned for the interpreter
            (stdin) based input.
        """
        if path == "<stdin>":
            return "shell"
        if os.name == "nt":
            path = os.path.splitdrive(path)[1]
        # This presumes we work through a virtual environment. This is
        # a safe assumption as we peruse through the site-packages.
        # In case this is not running via the virtual env, we might
        # get a different result.
        abspath = "site-packages" if "site-packages" in path else os.getcwd()
        path = path.split(abspath)[-1].replace(os.path.sep, ".")[
            path[0] != ":" : -3
        ]
        if fnc not in ("<module>", "<lambda>"):
            path += f".{fnc}"
        return path

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as text.

        If any exception is captured then it is formatted using the
        :py:meth:`ANSIFormatter.formatException()` and replaced with
        the original message.

        :param record: Instance of the logged event.
        :return: Captured and formatted output log string.
        """
        # Update the pathname and the invoking function name using the
        # stack. This stack will be set as a record attribute which will
        # allow us to use the %(stack)s placeholder in the log format.
        setattr(record, "stack", self.stack(record.pathname, record.funcName))
        if record.exc_info:
            record.msg = self.formatException(record.exc_info)
            record.exc_info = record.exc_text = None
        self.colorize(record)
        msg = logging.Formatter(self.fmt, self.datefmt).format(record)
        # Escape the ANSI sequence here as this will render the colors
        # on the TTY but won't add them to the non-TTY interfaces.
        record.msg = esc.sub("", str(record.msg))
        self.decolorize(record)
        return msg


class Handler:
    """
    Handler instances which dispatches logging events to streams.

    This is the base handler class which acts as a placeholder to
    define the handler interface. This class can optionally use a
    formatter to format the records.

    :param handler: Handler instance which will output to a stream.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to be used for formatting
        record, defaults to :py:class:`ANSIFormatter`.

    .. code-block:: python

        >>> import logging.handlers as handlers
        >>>
        >>> class CustomHandler(Handler):
        ...     def __init__(self, level, formatter, **kwargs):
        ...         handler = handlers.RotatingFileHandler(kwargs)
        ...         super().__init__(handler, level, formatter)
        ...     def do_rollover(self):
        ...         return self.handler.doRollover()

    .. versionadded:: 1.0.0
    """

    def __init__(
        self,
        handler: logging.Handler,
        level: t.Optional[t.Union[int, str]] = None,
        formatter: logging.Formatter = ANSIFormatter,  # type: ignore
    ) -> None:
        """Initialize the handler class."""
        self.handler = handler
        self.handler.setFormatter(formatter)
        if level:
            self.handler.setLevel(level)

    def add_handler(self, logger: logging.Logger) -> None:
        """Add handler to the logger object."""
        logger.addHandler(self.handler)


class RotatingFileHandler(Handler):
    """
    Handler instance for logging to a set of files which switch from
    one file to the next when the current file reaches a certain size.

    By default, the file grows indefinitely. You can specify particular
    values to allow the file to rollover at a pre-determined size.

    :param filename: Absolute path of the log file.
    :param mode: Mode in which the file needs to be opened, defaults to
        append mode.
    :param max_bytes: Maximum size in bytes after which the rollover
        should happen, defaults to 10 MB.
    :param backups: Maximum files to retain after rollover, defaults
        to 5.
    :param encoding: Platform-dependent encoding for the file, defaults
        to None.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to be used for formatting
        record, defaults to :py:class:`ANSIFormatter`.

    .. note::

        Rollover occurs whenever the current log file is nearly
        ``max_bytes`` in size. If the ``backups`` >= 1, the system will
        successively create new files with same pathname as the base
        file, but with extensions ".1", ".2", etc. appended to it. For
        example, with a ``backups`` count of 5 and a base file name of
        "xames3.log", "xames3.log.1", "xames3.log.2", ... through to
        "xames3.log.5" will be created. The file being written to is
        always "xames3.log". When it gets filled up, it is closed and
        renamed to "xames3.log.1" and if files "xames3.log.1",
        "xames3.log.2" etc. exists, then they are renamed to
        "xames3.log.2", "xames3.log.3", etc. respectively.

    .. note::

        If ``max_bytes`` is zero, rollover never occurs.

    .. seealso::

        :py:class:`Handler`
        :py:class:`logging.handlers.RotatingFileHandler`

    .. versionadded:: 1.0.0
    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        max_bytes: int = 10000000,
        backups: int = 5,
        encoding: t.Optional[str] = None,
        level: t.Optional[t.Union[int, str]] = None,
        formatter: logging.Formatter = ANSIFormatter,  # type: ignore
    ) -> None:
        """Open the file and use it as the stream for logging."""
        handler = handlers.RotatingFileHandler(
            filename, mode, max_bytes, backups, encoding
        )
        super().__init__(handler, level, formatter)

    def do_rollover(self) -> t.Any:
        """Do a rollover when current log file is nearly in size."""
        return self.handler.doRollover()  # type: ignore


class TTYInspector(logging.StreamHandler):
    """
    StreamHandler derivative which inspects if the output stream is a
    TTY or not.

    .. seealso::

        :py:meth:`logging.StreamHandler.format()`

    .. versionadded:: 1.0.0
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Add hint if the specified stream is a TTY.

        The ``hint`` here, means the total answer in reality as this
        attribute helps to identify a stream's interface. This solves
        a major problem of printing un-readable ANSI sequences to a
        non-TTY interface.

        :param record: Instance of the logged event.
        :return: Formatter string for the output stream.
        """
        if hasattr(self.stream, "isatty"):
            try:
                setattr(record, "isatty", self.stream.isatty())  # type: ignore
            except ValueError:
                setattr(record, "isatty", False)
        else:
            setattr(record, "isatty", False)
        strict = super().format(record)
        delattr(record, "isatty")
        return strict


class StreamHandler(Handler):
    """
    Handler class which writes appropriately formatted logging records
    to a TTY stream.

    :param stream: IO stream, defaults to sys.stderr.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to be used for formatting
        record, defaults to :py:class:`ANSIFormatter`.

    .. note::

        This class does not close the stream, as ``sys.stdout`` or
        ``sys.stderr`` may be used.

    .. seealso::

        :py:class:`Handler`

    .. versionadded:: 1.0.0
    """

    def __init__(
        self,
        stream: t.Optional[t.IO[str]] = sys.stderr,
        level: t.Optional[t.Union[int, str]] = None,
        formatter: logging.Formatter = ANSIFormatter,  # type: ignore
    ) -> None:
        """Initialize the stream handlers."""
        super().__init__(TTYInspector(stream), level, formatter)


stderr = StreamHandler()
stdout = StreamHandler(sys.stdout)


class Logger(logging.LoggerAdapter):
    """
    Logger instance to represent a logging channel.

    This instance uses a ``LoggerAdapter`` which makes it easier to
    specify contextual information in logging output.

    .. seealso::

         :py:class:`logging.LoggerAdapter`
         :py:meth:`logging.LoggerAdapter.process()`

    .. versionadded:: 1.0.0
    """

    def process(
        self, msg: t.Any, kwargs: t.MutableMapping[str, t.Any]
    ) -> t.Tuple[t.Any, t.MutableMapping[str, t.Any]]:
        """
        Process the logging message and the passed keyword arguments
        to a logging call to insert contextual information.

        You can either manipulate the message itself, the keyword
        arguments or both. Return the message and modified kwargs to
        suit your neeeds.

        :param msg: Logged message.
        :returns: Tuple of message and modified kwargs.
        """
        extra = self.extra.copy()  # type: ignore
        if "extra" in kwargs:
            extra.update(kwargs.pop("extra"))
        for name in kwargs.keys():
            if name == "exc_info":
                continue
            extra[name] = kwargs.pop(name)
        kwargs["extra"] = extra
        return msg, kwargs

    def debug(self, msg: t.Any, *args: t.Any, **kwargs: t.Any) -> None:
        """Log message with ``DEBUG`` severity level."""
        self.logger._log(10, msg, args, **kwargs)

    def info(self, msg: t.Any, *args: t.Any, **kwargs: t.Any) -> None:
        """Log message with ``INFO`` severity level."""
        self.logger._log(20, msg, args, **kwargs)

    def warning(self, msg: t.Any, *args: t.Any, **kwargs: t.Any) -> None:
        """Log message with ``WARNING`` severity level."""
        self.logger._log(30, msg, args, **kwargs)

    def error(self, msg: t.Any, *args: t.Any, **kwargs: t.Any) -> None:
        """Log message with ``ERROR`` severity level."""
        self.logger._log(40, msg, args, **kwargs)

    def critical(self, msg: t.Any, *args: t.Any, **kwargs: t.Any) -> None:
        """Log message with ``CRITICAL`` severity level."""
        self.logger._log(50, msg, args, **kwargs)

    def exception(self, msg: t.Any, *args: t.Any, **kwargs: t.Any) -> None:
        """Log message with ``CRITICAL`` severity level."""
        self.logger._log(60, msg, args, True, **kwargs)

    fatal = critical
    warn = warning
    trace = exception


def getLogger(name: t.Optional[str] = None, **kwargs: t.Any) -> Logger:
    """
    Return a logger with the specified name.

    :param name: Logging channel name, defaults to None.
    :returns: Logger instance.

    .. code-block:: python

        >>> logger = getLogger(__name__)
        >>> logger.info("hello hello")
        2021-09-18T10:59:47Z   INFO workspace...:23 : hello hello
        >>>

    .. seealso::

        :py:func:`logging.getLogger`

    .. versionadded:: 1.0.0
    """
    return Logger(logging.getLogger(name), kwargs)


def basicConfig(**kwargs: t.Any) -> Logger:
    """
    Do basic configuration for the logging system.

    The default behavior of this function is to create a
    ``RotatingFileHandler`` and ``StreamHandler`` instance which
    writes to an output log file and sys.stderr respectively and then
    set level for logging events to the handlers.

    A number of optional keyword arguments may be specified, which can
    alter the default behaviour.

    :returns: Logger instance.

    .. code-block:: python

        >>> logger = basicConfig(filename="xa.log", fmt=...)
        >>> logger.info("hello hello")
        2021-09-18T10:59:47Z   INFO workspace...:23 : hello hello
        >>>

    .. note::

        This implementation is based on :py:func:`logging.basicConfig`.

    .. versionadded:: 1.0.0
    """
    root = logging.getLogger(None)
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
    if len(root.handlers) == 0:
        level = kwargs.get("level", logging.INFO)
        root.setLevel(level)
        format = kwargs.get("format", None)
        datefmt = kwargs.get("datefmt", None)
        formatter = ANSIFormatter(format, datefmt)
        handlers = kwargs.get("handlers", None)
        if handlers is None:
            handlers = []
            stream = kwargs.get("stream", None)
            handlers.append(StreamHandler(stream, level, formatter))
            filename = kwargs.get("filename", None)
            filemode = kwargs.get("filemode", "a")
            if filename:
                handlers.append(
                    RotatingFileHandler(
                        filename, filemode, level=level, formatter=formatter
                    )
                )
        for handler in handlers:
            handler.add_handler(root)  # type: ignore
        capture_warnings = kwargs.get("capture_warnings", True)
        logging.captureWarnings(capture_warnings)
    name = kwargs.get("name", None)
    return getLogger(name, **kwargs)


class ANSIRequestHandler(WSGIRequestHandler):
    """
    A custom request handler that implements WSGI dispatching.

    This Werkzeug WSGI request handler works fine and returns desirable
    output but this seems little inconsistent with rest of the logs.
    Since we have a pre-defined log message format, we expect the
    werkzeug logs to adhere to our standards, we monkey patch the logs
    to better fit our needs.

    .. seealso::

        :py:class:`werkzeug.serving.WSGIRequestHandler`

    .. versionadded:: 1.0.0
    """

    def log(self, type: str, message: str, *args: t.Any) -> None:
        """Overridden implementation."""
        _log(type, message)

    def log_request(
        self, code: t.Union[int, str] = "-", size: t.Union[int, str] = "-"
    ) -> None:
        """Overridden implementation."""
        path = uri_to_iri(self.path)
        code = str(code)
        if code[0] == "1":
            attr = logging._levelToName[10]
        elif code == "200":
            attr = logging._levelToName[20]
        elif code == "304" or code[0] == "3":
            attr = logging._levelToName[30]
        elif code == "404" or code[0] == "4":
            attr = logging._levelToName[40]
        else:
            attr = logging._levelToName[50]
        try:
            fnc = f"{self.routes[path]}()"  # type: ignore
        except KeyError:
            fnc = "a non-existent function"
        self.log(
            attr.lower(),
            f"Mapped URL path [{path}] to {fnc} onto method of type "
            f"{self.command} [{code}] ({self.request_version.lower()})",
        )

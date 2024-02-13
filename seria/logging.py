import contextlib
import logging
import logging.handlers
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

__all__ = ("setup_logging",)


@contextlib.contextmanager
def setup_logging(level: int, loggers_to_disable: "Sequence[str]") -> "Generator[None, None, None]":
    log = logging.getLogger()

    try:
        discord.utils.setup_logging()

        max_bytes = 32 * 1024 * 1024
        logging.getLogger("discord").setLevel(level)

        for logger in loggers_to_disable:
            logging.getLogger(logger).setLevel(logging.WARNING)

        log.setLevel(level)

        handler = logging.handlers.RotatingFileHandler(
            filename="hoyo_buddy.log",
            encoding="utf-8",
            mode="w",
            maxBytes=max_bytes,
            backupCount=5,
        )
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        fmt = logging.Formatter("[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{")
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        handlers = log.handlers[:]
        for handler in handlers:
            handler.close()
            log.removeHandler(handler)

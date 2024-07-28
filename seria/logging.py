import contextlib
import logging
import logging.handlers
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

__all__ = ("setup_logging",)


@contextlib.contextmanager
def setup_logging(
    level: int,
    *,
    loggers_to_suppress: "Sequence[str] | None" = None,
    log_filename: str = "log.log",
) -> "Generator[None, None, None]":
    log = logging.getLogger()

    try:
        import discord

        discord.utils.setup_logging()

        max_bytes = 32 * 1024 * 1024
        logging.getLogger("discord").setLevel(logging.INFO)

        if loggers_to_suppress is not None:
            for logger in loggers_to_suppress:
                logging.getLogger(logger).setLevel(logging.CRITICAL)

        log.setLevel(level)

        handler = logging.handlers.RotatingFileHandler(
            filename=log_filename,
            encoding="utf-8",
            mode="w",
            maxBytes=max_bytes,
            backupCount=5,
        )
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        fmt = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
        )
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        handlers = log.handlers[:]
        for handler in handlers:
            handler.close()
            log.removeHandler(handler)

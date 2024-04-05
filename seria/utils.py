import asyncio
import os
import re
from typing import Any, TypeVar

import aiofiles
import orjson
import yaml

from .constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS

__all__ = (
    "clean_url",
    "create_bullet_list",
    "extract_image_urls",
    "extract_media_urls",
    "extract_urls",
    "extract_video_urls",
    "read_json",
    "read_yaml",
    "shorten",
    "split_list_to_chunks",
    "write_json",
    "write_yaml",
)

T = TypeVar("T")
locks: dict[str, asyncio.Lock] = {}


def clean_url(url: str) -> str:
    """Remove query parameters from the URL."""
    return url.split("?")[0]


def split_list_to_chunks(lst: list[T], chunk_size: int) -> list[list[T]]:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def extract_urls(text: str, *, clean: bool = True) -> list[str]:
    urls = re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text
    )
    if clean:
        return [clean_url(url) for url in urls]
    return urls


def extract_image_urls(text: str, *, clean: bool = True) -> list[str]:
    return [
        url for url in extract_urls(text, clean=clean) if clean_url(url).endswith(IMAGE_EXTENSIONS)
    ]


def extract_video_urls(text: str, *, clean: bool = True) -> list[str]:
    return [
        url for url in extract_urls(text, clean=clean) if clean_url(url).endswith(VIDEO_EXTENSIONS)
    ]


def extract_media_urls(text: str, *, clean: bool = True) -> list[str]:
    return extract_image_urls(text, clean=clean) + extract_video_urls(text, clean=clean)


async def _read_file(
    path: str,
    encoding: str = "utf-8",
    handle_file_not_found: bool = True,
    ignore_lock: bool = False,
) -> Any:
    lock = locks.setdefault(path, asyncio.Lock()) if not ignore_lock else asyncio.Lock()
    try:
        async with lock, aiofiles.open(path, mode="r", encoding=encoding) as file:
            if path.endswith(".json"):
                return orjson.loads(await file.read())
            elif path.endswith(".yaml"):
                return yaml.safe_load(await file.read())
            else:
                return await file.read()
    except FileNotFoundError:
        if handle_file_not_found:
            return {}
        raise


async def _write_file(
    path: str, data: Any, encoding: str = "utf-8", ignore_lock: bool = False
) -> None:
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    lock = locks.setdefault(path, asyncio.Lock()) if not ignore_lock else asyncio.Lock()
    async with lock, aiofiles.open(path, mode="w", encoding=encoding) as file:
        if path.endswith(".json"):
            await file.write(orjson.dumps(data).decode(encoding))
        elif path.endswith(".yaml"):
            await file.write(yaml.dump(data))
        else:
            await file.write(data)


async def read_yaml(
    path: str,
    *,
    encoding: str = "utf-8",
    handle_file_not_found: bool = True,
    ignore_lock: bool = False,
) -> Any:
    await _read_file(
        path,
        encoding=encoding,
        handle_file_not_found=handle_file_not_found,
        ignore_lock=ignore_lock,
    )


async def write_yaml(
    path: str,
    data: dict,
    *,
    encoding: str = "utf-8",
    ignore_lock: bool = False,
) -> None:
    await _write_file(path, data, encoding=encoding, ignore_lock=ignore_lock)


async def read_json(
    path: str,
    *,
    encoding: str = "utf-8",
    handle_file_not_found: bool = True,
    ignore_lock: bool = False,
) -> Any:
    await _read_file(
        path,
        encoding=encoding,
        handle_file_not_found=handle_file_not_found,
        ignore_lock=ignore_lock,
    )


async def write_json(
    path: str, data: Any, *, encoding: str = "utf-8", ignore_lock: bool = False
) -> None:
    await _write_file(path, data, encoding=encoding, ignore_lock=ignore_lock)


def shorten(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[: length - 3] + "..."


def create_bullet_list(input_list: list[str]) -> str:
    return "\n".join(["* " + item for item in input_list])

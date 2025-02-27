import asyncio
import os
import pathlib
import re
import weakref
from typing import Any, TypeVar

import yarl

from .constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS

__all__ = (
    "clean_url",
    "split_list_to_chunks",
    "extract_urls",
    "extract_image_urls",
    "extract_video_urls",
    "extract_media_urls",
    "read_yaml",
    "write_yaml",
    "read_json",
    "write_json",
    "shorten",
    "create_bullet_list",
)

T = TypeVar("T")

locks: weakref.WeakValueDictionary[str, asyncio.Lock] = weakref.WeakValueDictionary()


def clean_url(url: str) -> str:
    """Remove query parameters from the URL."""
    return url.split("?")[0]


def split_list_to_chunks(lst: list[T], chunk_size: int) -> list[list[T]]:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def extract_urls(text: str, *, clean: bool = True) -> list[str]:
    urls = re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text,
    )
    if clean:
        return [clean_url(url) for url in urls]
    return urls


def extract_image_urls(text: str, *, clean: bool = True) -> list[str]:
    return [
        url
        for url in extract_urls(text, clean=clean)
        if clean_url(url).endswith(IMAGE_EXTENSIONS)
    ]


def extract_video_urls(text: str, *, clean: bool = True) -> list[str]:
    return [
        url
        for url in extract_urls(text, clean=clean)
        if clean_url(url).endswith(VIDEO_EXTENSIONS)
    ]


def extract_media_urls(text: str, *, clean: bool = True) -> list[str]:
    return extract_image_urls(text, clean=clean) + extract_video_urls(text, clean=clean)


async def _read_file(
    path: pathlib.Path | str,
    encoding: str = "utf-8",
    *,
    handle_file_not_found: bool = True,
    ignore_lock: bool = False,
) -> Any:
    import aiofiles
    import orjson
    import yaml

    lock = (
        locks.setdefault(str(path), asyncio.Lock())
        if not ignore_lock
        else asyncio.Lock()
    )
    try:
        async with lock, aiofiles.open(path, mode="r", encoding=encoding) as file:
            if str(path).endswith(".json"):
                return orjson.loads(await file.read())
            elif str(path).endswith(".yaml"):
                return yaml.safe_load(await file.read())
            else:
                return await file.read()
    except FileNotFoundError:
        if handle_file_not_found:
            return {}
        raise


async def _write_file(
    path: pathlib.Path | str,
    data: Any,
    encoding: str = "utf-8",
    ignore_lock: bool = False,
) -> None:
    if not os.path.exists(os.path.dirname(path)) and os.path.dirname(path):
        os.makedirs(os.path.dirname(path))

    import aiofiles
    import orjson
    import yaml

    lock = (
        locks.setdefault(str(path), asyncio.Lock())
        if not ignore_lock
        else asyncio.Lock()
    )
    async with lock, aiofiles.open(path, mode="w", encoding=encoding) as file:
        if str(path).endswith(".json"):
            await file.write(orjson.dumps(data).decode(encoding))
        elif str(path).endswith(".yaml"):
            await file.write(yaml.dump(data, allow_unicode=True))
        else:
            await file.write(data)


async def read_yaml(
    path: pathlib.Path | str,
    *,
    encoding: str = "utf-8",
    handle_file_not_found: bool = True,
    ignore_lock: bool = False,
) -> Any:
    return await _read_file(
        path,
        encoding=encoding,
        handle_file_not_found=handle_file_not_found,
        ignore_lock=ignore_lock,
    )


async def write_yaml(
    path: pathlib.Path | str,
    data: dict,
    *,
    encoding: str = "utf-8",
    ignore_lock: bool = False,
) -> None:
    await _write_file(path, data, encoding=encoding, ignore_lock=ignore_lock)


async def read_json(
    path: pathlib.Path | yarl.URL | str,
    *,
    encoding: str = "utf-8",
    handle_file_not_found: bool = True,
    ignore_lock: bool = False,
) -> Any:
    if not isinstance(path, pathlib.Path) and (
        isinstance(path, yarl.URL) or extract_urls(path)
    ):
        import aiohttp
        import orjson

        async with aiohttp.ClientSession() as session:
            async with session.get(path) as response:
                if response.content_type == "text/plain":
                    return orjson.loads(await response.text(encoding=encoding))
                return await response.json(encoding=encoding, loads=orjson.loads)

    return await _read_file(
        path,
        encoding=encoding,
        handle_file_not_found=handle_file_not_found,
        ignore_lock=ignore_lock,
    )


async def write_json(
    path: pathlib.Path | str,
    data: Any,
    *,
    encoding: str = "utf-8",
    ignore_lock: bool = False,
) -> None:
    await _write_file(path, data, encoding=encoding, ignore_lock=ignore_lock)


def shorten(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[: length - 3] + "..."


def create_bullet_list(input_list: list[str]) -> str:
    return "\n".join(["* " + item for item in input_list])

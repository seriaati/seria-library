import re
from typing import Any, TypeVar

import aiofiles
import orjson
import yaml
from constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS

__all__ = (
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


def split_list_to_chunks(lst: list[T], chunk_size: int) -> list[list[T]]:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def extract_urls(text: str) -> list[str]:
    return re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text
    )


def extract_image_urls(text: str) -> list[str]:
    return [url for url in extract_urls(text) if url.endswith(IMAGE_EXTENSIONS)]


def extract_video_urls(text: str) -> list[str]:
    return [url for url in extract_urls(text) if url.endswith(VIDEO_EXTENSIONS)]


def extract_media_urls(text: str) -> list[str]:
    return extract_image_urls(text) + extract_video_urls(text)


async def read_yaml(path: str, *, encoding: str = "utf-8") -> Any:
    async with aiofiles.open(path, mode="r", encoding=encoding) as file:
        return yaml.safe_load(await file.read())


async def write_yaml(path: str, data: dict, *, encoding: str = "utf-8") -> None:
    async with aiofiles.open(path, mode="w", encoding=encoding) as file:
        await file.write(yaml.dump(data))


async def read_json(path: str, *, encoding: str = "utf-8") -> Any:
    async with aiofiles.open(path, mode="r", encoding=encoding) as file:
        return orjson.loads(await file.read())


async def write_json(path: str, data: Any, *, encoding: str = "utf-8") -> None:
    async with aiofiles.open(path, mode="w", encoding=encoding) as file:
        await file.write(orjson.dumps(data).decode(encoding))


def shorten(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[: length - 3] + "..."


def create_bullet_list(input_list: list[str]) -> str:
    return "\n".join(["* " + item for item in input_list])

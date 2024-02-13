from typing import Any, Self

from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.models import Model as TortoiseModel

__all__ = ("Model",)


class Model(TortoiseModel):
    @classmethod
    async def get_or_create(cls, **kwargs: Any) -> tuple[Self, bool]:
        try:
            return await cls.get(**kwargs), False
        except DoesNotExist:
            return await cls.create(**kwargs), True

    @classmethod
    async def silent_create(cls, **kwargs: Any) -> Self | None:
        try:
            return await cls.create(**kwargs)
        except IntegrityError:
            return None

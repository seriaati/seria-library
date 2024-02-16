from typing import Any, Self

from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.models import Model as TortoiseModel

__all__ = ("Model",)


class Model(TortoiseModel):
    @classmethod
    async def get_or_create(cls, **kwargs: Any) -> tuple[Self, bool]:
        """Get an instance of the model by the given parameters or create it if it doesn't exist."""
        try:
            return await cls.get(**kwargs), False
        except DoesNotExist:
            return await cls.create(**kwargs), True

    @classmethod
    async def silent_create(cls, **kwargs: Any) -> Self | None:
        """Create an instance of the model with the given parameters or return None if it already exists."""
        try:
            return await cls.create(**kwargs)
        except IntegrityError:
            return None

    async def silent_save(self, **kwargs: Any) -> bool:
        """Save the instance or return False if it already exists."""
        try:
            await self.save(**kwargs)
        except IntegrityError:
            return False
        else:
            return True

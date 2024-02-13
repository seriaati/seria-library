from typing import Any, Generic, TypeVar

import discord
from discord import ui

from ..utils import split_list_to_chunks

__all__ = ("NEXT_PAGE", "PREV_PAGE", "PaginatorSelect")

V = TypeVar("V", bound=ui.View)

NEXT_PAGE = discord.SelectOption(label="Next page", value="next_page")
PREV_PAGE = discord.SelectOption(label="Previous page", value="prev_page")


class PaginatorSelect(ui.Select, Generic[V]):
    def __init__(
        self,
        options: list[discord.SelectOption],
        *,
        next_page: discord.SelectOption = NEXT_PAGE,
        prev_page: discord.SelectOption = PREV_PAGE,
        **kwargs,
    ) -> None:
        self.split_options = split_list_to_chunks(options, 23)
        self.page_index = 0
        self.next_page = next_page
        self.prev_page = prev_page

        super().__init__(options=self._process_options(), **kwargs)
        self.view: V

    def _process_options(self) -> list[discord.SelectOption]:
        if self.page_index == 0:
            if len(self.split_options) == 1:
                return self.split_options[0]
            return self.split_options[0] + [self.next_page]
        if self.page_index == len(self.split_options) - 1:
            return [self.prev_page] + self.split_options[-1]
        return [self.prev_page] + self.split_options[self.page_index] + [self.next_page]

    async def callback(self) -> Any:
        if self.values[0] == "next_page":
            self.page_index += 1
            self.options = self._process_options()
        elif self.values[0] == "prev_page":
            self.page_index -= 1
            self.options = self._process_options()

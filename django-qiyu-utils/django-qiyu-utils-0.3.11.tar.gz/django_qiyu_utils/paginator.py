import warnings
from typing import Iterable

from django.core.paginator import Paginator, Page

__all__ = ["CustomPaginator"]

warnings.warn(
    "CustomPage is deprecated use Page.get_elided_page_range method instead",
    DeprecationWarning,
)


class CustomPage(Page):
    max_show_pages = 9

    def show_page_start_index(self) -> int:
        assert isinstance(self.paginator, CustomPaginator)
        start = 1
        end = self.paginator.num_pages
        if end <= self.max_show_pages:
            return start
        if self.number - self._show_half_size() <= start:
            return start
        return self.number - self._show_half_size()

    def show_page_end_index(self) -> int:
        assert isinstance(self.paginator, CustomPaginator)
        real_end = self.paginator.num_pages
        expect_end = self.number + self._show_half_size()

        if real_end <= self.max_show_pages:  # 实际有的没有 需要展示的多
            return real_end

        if expect_end >= real_end:  # 期望的太多 超过实际有的
            return real_end

        if expect_end < self.max_show_pages:
            return self.max_show_pages

        return self.number + self._show_half_size()

    def show_page_have_previous_ellipse(self) -> bool:
        if self.number - self._show_half_size() > 1:
            return True
        return False

    def show_page_have_next_ellipse(self) -> bool:
        assert isinstance(self.paginator, CustomPaginator)
        if self.number + self._show_half_size() < self.paginator.num_pages:
            return True
        return False

    def show_page_range(self) -> Iterable[int]:
        return range(self.show_page_start_index(), self.show_page_end_index() + 1)

    def _show_half_size(self) -> int:
        return int(self.max_show_pages / 2)


class CustomPaginator(Paginator):
    def page(self, number) -> CustomPage:
        return super().page(number)

    def _get_page(self, *args, **kwargs) -> CustomPage:
        return CustomPage(*args, **kwargs)

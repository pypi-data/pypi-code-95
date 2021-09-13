from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

__all__ = ["RedirectHelper"]


class RedirectHelper(object):
    """
    重定向辅助
    """

    @staticmethod
    def to_url(request: HttpRequest, default_url: str, next_param: str = "next") -> str:
        """
        获取需要跳转到的 URL
        """
        # noinspection PyTypeChecker
        gn = request.GET.get(next_param, None)
        if gn is not None:
            return gn

        # noinspection PyTypeChecker
        pn = request.POST.get(next_param, None)
        if pn is not None:
            return pn

        return default_url

    @staticmethod
    def to_page(
        request: HttpRequest, default_url: str, next_param: str = "next"
    ) -> HttpResponse:
        """
        跳转到 request 指定的页面 或者 默认的页面
        """
        url = RedirectHelper.to_url(request, default_url, next_param)
        return redirect(url)

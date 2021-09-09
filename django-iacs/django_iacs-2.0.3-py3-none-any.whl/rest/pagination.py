from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationExtension(PageNumberPagination):
    page_size_query_param = "page_size"

    # default_page_size = 20
    #
    # def get_page_size(self, request):
    #     """
    #     ### 重写方法，当没有page_size的时候返回默认的page_size，达到默认返回分页数据的目的
    #
    #     :param request:
    #     :return:
    #     """
    #
    #     page_size = super(PageNumberPaginationExtension, self).get_page_size(request)
    #     if page_size is None:
    #         self.page_size = self.default_page_size
    #     else:
    #         self.page_size = page_size
    #
    #     return self.page_size

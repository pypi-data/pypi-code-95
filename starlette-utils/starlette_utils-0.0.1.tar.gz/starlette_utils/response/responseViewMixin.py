from starlette_utils.response.response_results import success_result, error_result


class ResponseViewMixin(object):
    # settings已配置，本处无需重复配置
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    # pagination_classes = RestPagination

    def success(self, data):
        """
        成功响应

        :param data:
        :return:
        """
        return success_result(data)

    def error(self, message: str = 'failed', code: int = 1001, status_code: int = 502):
        """
        失败响应

        :param message:
        :param code:
        :param status_code:
        :return:
        """
        return error_result(message=message, code=code, status_code=status_code)

    def get_queryset(self):
        """
        筛选有效数据
        """
        assert self.model_class is not None, (
            "model_class is required or override the `get_queryset()` method."
        )

        queryset = self.model_class.all()
        if hasattr(self.model_class, 'is_delete'):
            return queryset.filter(is_delete=False)
        else:
            return queryset

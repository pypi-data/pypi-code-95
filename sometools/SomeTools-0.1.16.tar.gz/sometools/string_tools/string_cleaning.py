class GeneralString:

    def __init__(self, *args, **kwargs):
        super(GeneralString, self).__init__(*args, **kwargs)

    @staticmethod
    def clean_string(temp_string: str) -> str:
        """
        去掉空格回车换行等
        :param temp_string: str
        :return: str
        """
        if temp_string:
            _temp_str = ''.join(temp_string).replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('\\r', '').replace('\\n', '').replace('\\t', '')
            return str(_temp_str.strip())
        else:
            return ''

    @staticmethod
    def clean_string_without_space(temp_string: str) -> str:
        """
        去掉回车换行等但是保留空格
        :param temp_string: str
        :return: str
        """
        if temp_string:
            _temp_str = ''.join(temp_string).replace('\r', '').replace('\n', '').replace('\t', '').replace('\\r', '').replace('\\n', '').replace('\\t', '')
            return str(_temp_str.strip())
        else:
            return ''

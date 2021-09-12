from cubic.rest import Rest


class SqreamClient:
    __rest: Rest
    __server: str
    __user: dict
    __token_key: str

    def __init__(self, server: str, user: dict, token_key: str):
        self.__server = server
        self.__user = user
        self.__token_key = token_key
        self.__rest = Rest(server=self.__server)

    def tables(self):
        return self.__rest.post("sqream/tables", {
            'user': self.__user,
            'tokenKey': self.__token_key,
        })

    def table(self, table_name: str, where: str = "", order_by: str = "", limit: int = 0, columns=None):
        if columns is None:
            columns = []
        return self.__rest.post("sqream/table", {
            'user': self.__user,
            'tokenKey': self.__token_key,
            'tableName': table_name,
            'where': where,
            'orderBy': order_by,
            'limit': limit,
            'columns': columns
        })

from esu.base import BaseAPI, Field, ObjectHasNoId


class PubKey(BaseAPI):
    """
    Args:
        id (str): Идентификатор публичного ключа
        name (str): Имя публичного ключа
        public_key (str): Публичный ключ
        fingerprint (str): fingerprint публичного ключа
    """
    class Meta:
        id = Field()
        name = Field()
        public_key = Field()
        fingerprint = Field()

    @classmethod
    def get_object(cls, id, token=None):
        """
        Получить объект публичного ключа по его ID

        Args:
            id (str): Идентификатор публичного ключа
            token (str): Токен для доступа к API. Если не передан, будет
                         использована переменная окружения **ESU_API_TOKEN**

        Returns:
            object: Возвращает объект публичного ключа :class:`esu.Disk`
        """
        pub_key = cls(token=token, id=id)
        pub_key._get_object('v1/account/me/key', pub_key.id)
        return pub_key

    def save(self):
        """
        Сохранить изменения

        Raises:
            ObjectHasNoId: Если производится попытка сохранить несуществующий
                           объект
        """
        if self.id is None:
            raise ObjectHasNoId

        self._commit()

    def _commit(self):
        self._commit_object('v1/account/me/key', name=self.name,
                            public_key=self.public_key)

    def destroy(self):
        """
        Удалить объект

        Raises:
            ObjectHasNoId: Когда производится попытка удалить несуществующий
                           объект
        """
        if self.id is None:
            raise ObjectHasNoId

        self._destroy_object('v1/account/me/key', self.id)
        self.id = None

from credmgr.models.utils import camelToSnake


class EditableMixin:
    _editableAttrs = []

    def edit(self, **kwargs):
        """Edit the object

        :param kwargs: The params to update on the object.

        :returns: The edited object.

        """
        payload = []

        for attr in self._editableAttrs:
            if attr in kwargs:
                if attr in self._apiNameMapping:
                    path = f"/{self._apiNameMapping[attr]}"
                else:
                    path = f"/{camelToSnake(attr)}"
                payload.append({"op": "replace", "path": path, "value": kwargs[attr]})
        self.__dict__.update(
            self._credmgr.patch(f"{self._path}/{self.id}", data=payload).__dict__
        )
        return self

from credmgr.models.utils import CachedProperty


class OwnerMixin:
    _editableAttrs = []

    @CachedProperty
    def owner(self):
        if not self._fetched:
            self._fetch()
        user = self._credmgr.user(id=self.ownerId)
        return user

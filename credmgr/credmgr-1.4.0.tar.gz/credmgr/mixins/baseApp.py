from ..mixins import BaseModel, DeletableMixin, EditableMixin, OwnerMixin


class BaseApp(BaseModel, DeletableMixin, EditableMixin, OwnerMixin):
    _attrTypes = {**BaseModel._attrTypes, "app_name": "str", "owner_id": "int"}
    _nameAttr = "name"
    _nameMapping = {"app_name": "name"}
    _editableAttrs = [
        "name",
    ]
    _apiNameMapping = {"name": "app_name"}

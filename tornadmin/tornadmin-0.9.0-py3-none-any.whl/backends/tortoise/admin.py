from tornadmin.backends.base import BaseModelAdmin
from tornadmin.backends.tortoise.forms import modelform_factory
from tornadmin.utils import split_camel, slugify, get_display_name


class ModelAdmin(BaseModelAdmin):
    def __init__(self, model, **kwargs):
        name = model.__name__

        self.model = model
        self.name = kwargs.get('name', ' '.join(split_camel(name)))
        self.slug = kwargs.get('slug', name.lower())
        self.app = kwargs['app']
        self.app_slug = slugify(self.app)

    def get_list_headers(self):
        headers = []
        for header in self.list_headers:
            if isinstance(header, tuple) or isinstance(header, list):
                headers.append(header)
            else:
                headers.append((header, get_display_name(header)))
        return headers

    async def get_list(self, request_handler):
        return await self.model.all().order_by('-id')

    async def get_object(self, request_handler, id):
        return await self.model.get(id=id)

    async def get_form_data(self, obj):
        """Returns initial form data from the given model object"""
        data = {}

        for field_name, model_field in obj._meta.fields_map.items():
            data[field_name] = getattr(obj, field_name)

        return data

    def get_form(self, request_handler):
        form = modelform_factory(self, self.model)
        return form

    async def save_model(self, request_handler, form, obj=None):
        if obj:
            for field in form._fields:
                setattr(obj, field, getattr(form, field).data)
            await obj.save()
        else:
            obj = await self.model.create(**form.data)
        return obj

from django.test import TestCase
from edc_dashboard.url_names import url_names

from ...wrappers import ModelWrapper
from ..models import Example, ParentExample


class TestFields(TestCase):
    @classmethod
    def setUpClass(cls):
        url_names.register("thenexturl", "thenexturl", "edc_model_wrapper")
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        url_names.registry.pop("thenexturl")
        super(TestFields, cls).tearDownClass()

    def test_fields_skips_example(self):
        model_obj = ParentExample.objects.create()
        wrapper = ModelWrapper(
            model_obj=model_obj, model_cls=ParentExample, next_url_name="thenexturl"
        )

        self.assertNotIn("example", dict(wrapper.field_values_as_strings))

    def test_fields_rel(self):
        model_obj = Example.objects.create()
        wrapper = ModelWrapper(
            model_obj=model_obj, model_cls=Example, next_url_name="thenexturl"
        )
        dct = wrapper.field_values_as_strings
        for k, v in dct:
            if k == "id":
                self.assertEqual(v, model_obj.pk)

    def test_fields_rel2(self):
        model_obj = ParentExample.objects.create()
        wrapper = ModelWrapper(
            model_obj=model_obj, model_cls=ParentExample, next_url_name="thenexturl"
        )
        dct = wrapper.field_values_as_strings
        for k, v in dct:
            if k == "id":
                self.assertEqual(v, model_obj.pk)

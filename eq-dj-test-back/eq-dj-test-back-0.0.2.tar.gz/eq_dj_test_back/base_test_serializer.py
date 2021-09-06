from django.test.testcases import TestCase
from django.urls.base import reverse
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
# from functools import partial
# from typing import Any, Dict

# from factory import Factory
# from factory.base import StubObject


class SerializerTestBase(TestCase):

    # def setUp(self):
    # incluir self.serializer y self.validated_data localmente

    # Ejecuta un metodo del serializer tomando sus respectivos parametros,
    def base_test_ser(self, metodo, **kwargs):
        aux = getattr(self.serializer, metodo)
        result = aux(self, **kwargs)
        return result

    # Este metodo compara el contenido de una instancia con los datos
    # que se ingresan para generarla; Si la instancia posee campos foreignkey
    # deben incluirse dichas claves en la lista [nested_pk] en
    # determinado orden (punto de mejora)
    def compare_content(self, instance, nested_pk=None):
        dic_instance = instance.__dict__
        cont = 0
        for key in self.validated_data:
            if isinstance(self.validated_data[key], dict):
                key2 = key + '_id'
                self.assertEqual(
                    self.validated_data[key][nested_pk[cont]],
                    dic_instance[key2]
                    )
                cont += 1
            else:
                self.assertEqual(self.validated_data[key], dic_instance[key])

    def context_definition(self, serializer, data):
        self.path = reverse(self.to_path)
        self.factory = APIRequestFactory()
        self.request = self.factory.get(self.path, data, format='json')
        ser = serializer(data=data, context={'request': Request(self.request)})
        self.context = ser.context

    # def generate_dict_factory(factory: Factory):
    #     def convert_dict_from_stub(stub: StubObject) -> Dict[str, Any]:
    #         stub_dict = stub.__dict__
    #         for key, value in stub_dict.items():
    #             if isinstance(value, StubObject):
    #                 stub_dict[key] = convert_dict_from_stub(value)
    #         return stub_dict

    #     def dict_factory(factory, **kwargs):          # esta parte requiere
    #         stub = factory.stub(**kwargs)             # factory boy
    #         stub_dict = convert_dict_from_stub(stub)
    #         return stub_dict

    #     return partial(dict_factory, factory)

from django.test.testcases import TestCase


class ModelTestBase(TestCase):

    # def setUp(self):
    # incluir self.instance localmente

    # Ejecuta un metodo del modelo tomando sus respectivos parametros,
    def base_test_model(self, metodo, assertion, **kwargs):
        aux = getattr(self.instance, metodo)
        result = aux(**kwargs)
        if assertion:
            self.assertEqual(result, assertion)
        return result

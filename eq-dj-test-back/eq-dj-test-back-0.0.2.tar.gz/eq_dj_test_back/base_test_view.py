import io
from PIL import Image
from django.contrib.auth.models import User
from django.urls.base import reverse
from rest_framework.test import APIRequestFactory, APITestCase, \
    force_authenticate
from django.test import override_settings
import tempfile
import shutil

# Crea directorio temporal para imagenes
MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ViewsTestBase(APITestCase):

    def setUp(self):
        # agregar en setUp local: self.data, self.user_pk, self.to_path,
        # self.view y self.args si hiciera falta

        self.factory = APIRequestFactory()
        self.user = User.objects.get(pk=self.user_pk)

    # Obtiene la url necesaria para elaborar el request
    def get_path(self, to_path, *args, **kwargs):
        if to_path != '':
            return reverse(to_path, *args, **kwargs)
        return ''

    # Elabora un request ya autenticado para un metodo especifico
    def get_request(self, metodo, data, path, format='json'):
        aux = getattr(self.factory, metodo)
        request = aux(path, data, format=format)
        force_authenticate(request, user=self.user)
        return request

    # Es la funcion base para testear las vistas
    # Requiere especificar el metodo del request
    # Los argumentos que podria requerir el path pueden coincidir con los
    # kwargs que pudiera requerir el view, esto seria lo mejor a mi entender

    def base_test_view(self, metodo, data, stat, path=get_path,
                       format='json', ret=False, **kwargs):
        request = self.get_request(metodo, data, path, format)
        result = self.view(request, **kwargs)
        self.assertEqual(stat, result.status_code)
        if ret:
            return result

    # Compara el contenido de un campo con un valor esperado
    def assert_field(self, pk, model, field, expected):
        aux = getattr(model, 'objects')
        instance = getattr(aux, 'get')(pk=pk)
        aux = getattr(model, '_meta')
        field_object = getattr(aux, 'get_field')(field)
        field_value = getattr(field_object, 'value_from_object')(instance)
        if hasattr(field_object, 'generate_filename'):
            self.assertIsNotNone(field_value)
        else:
            self.assertEqual(str(field_value), str(expected))

    # Borra directorios creados temporalmente
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    # usar con PIL instalado
    def generate_photo_file(self, file_name):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = file_name
        file.seek(0)
        return file

    # De los dos siguientes metodos podria sacarse mucho provecho
    # en lo que a vistas se refiere

    # Setea el view con parametros especificos, diferente del metodo as_view()
    def setup_view(view, request, *args, **kwargs):
        # view es la clase directamente sin .as_view(),
        # que es reemplazado por setup_view()
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

# Obtiene una respuesta a un request utilizando la funcion dispatch()
    def get_response(view):
        # view ya seteada como parametro
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        return response

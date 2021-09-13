import falcon
from falcon_cors import CORS
from frase.api.middleware import AuthenticationMiddleware
from frase.api.resources.generation import Generation
from frase.api.resources.info import Info
from frase.api.router import ROUTE


class Server:
    @property
    def app(self):
        api = None
        try:
            cors = CORS(
                allow_all_origins=True,
                allow_methods_list=["POST", "GET", "DELETE", "PUT"],
                allow_all_headers=True,
                allow_credentials_all_origins=True
            )

            api = app = falcon.API(middleware=[
                cors.middleware,
                AuthenticationMiddleware()
            ])

            api.add_route(ROUTE['generation'], Generation())
            api.add_route(ROUTE['info'], Info())

        except Exception as e:
            print(str(e))
        return api

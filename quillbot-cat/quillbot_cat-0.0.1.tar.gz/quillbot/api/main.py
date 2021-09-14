import falcon
from falcon_cors import CORS
from quillbot.api.middleware import AuthenticationMiddleware
from quillbot.api.resources.paraphrasing import Paraphrasing, FreeParaphrasing
from quillbot.api.router import ROUTE


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

            api.add_route(ROUTE['paraphrasing'], Paraphrasing())
            api.add_route(ROUTE['free_paraphrasing'], FreeParaphrasing())

        except Exception as e:
            print(str(e))
        return api

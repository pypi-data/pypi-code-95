import falcon
import ujson

from frase.frase_selenium.fraseio import Fraseio


class Info:
    def on_get(self, req, resp):
        user = req.context.get("user")
        token_user_uuid = user["sub"]

        try:
            fraseio = Fraseio()
            fraseio.authorize_user()
            res = fraseio.get_countries_and_languages()
            fraseio.driver.quit()
            resp.body = ujson.dumps(res)
        except Exception as e:
            raise falcon.HTTP_500(str(e), "Something went wrong")

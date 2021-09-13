import falcon
import ujson

from frase.frase_selenium.fraseio import Fraseio, InputDataValidator
from frase.utils import check_dict_attr, read_stream


class Generation:
    def on_post(self, req, resp):
        user = req.context.get("user")
        token_user_uuid = user["sub"]

        data = read_stream(req.stream)
        data = check_dict_attr(InputDataValidator, data, "Invalid input data")
        try:
            if all([data.query, data.lang, data.country, data.text_length]):
                fraseio = Fraseio()
                generated_text = fraseio.run(data)
                res = {
                    'generated_text': generated_text
                }
                resp.body = ujson.dumps(res)

                resp.status = falcon.HTTP_201
            else:
                raise falcon.HTTPBadRequest("Bad request", "Not all required fields are provided")
        except Exception as e:
            raise falcon.HTTP_500(str(e), "Something went wrong")

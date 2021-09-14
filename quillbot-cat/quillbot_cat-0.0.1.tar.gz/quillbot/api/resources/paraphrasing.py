import falcon
import ujson

from quillbot.quillbot_selenium.quillbot_scripts import Quillbot, InputDataValidator
from quillbot.utils import check_dict_attr, read_stream
from selenium.common.exceptions import WebDriverException


class Paraphrasing:
    def on_post(self, req, resp):
        user = req.context.get("user")
        token_user_uuid = user["sub"]
        data = read_stream(req.stream)
        data = check_dict_attr(InputDataValidator, data, "Invalid input data")
        bot = Quillbot()
        try:
            if data.text:
                bot.authorize_user()
                paraphrased_text = bot.paraphrase_all_content(data.text)
                bot.driver.quit()
                res = {
                    'paraphrased_text': paraphrased_text
                }
                resp.body = ujson.dumps(res)
                resp.status = falcon.HTTP_201
            else:
                raise falcon.HTTPBadRequest("Bad request", "Not all required fields are provided")
        except WebDriverException:
            bot.driver.quit()
            raise falcon.HTTPBadRequest("Bad request", "There was some issues with Selenium scripts' processes")
        except Exception:
            bot.driver.quit()
            raise falcon.HTTPBadRequest('Bad request', "Something went wrong")


class FreeParaphrasing:
    def on_post(self, req, resp):
        user = req.context.get("user")
        token_user_uuid = user["sub"]

        data = read_stream(req.stream)
        data = check_dict_attr(InputDataValidator, data, "Invalid input data")
        bot = Quillbot()

        try:
            if data.text:
                paraphrased_text = bot.paraphrase_all_content_free(data.text)
                bot.driver.quit()
                res = {
                    'paraphrased_text': paraphrased_text
                }
                resp.body = ujson.dumps(res)
                resp.status = falcon.HTTP_201
            else:
                raise falcon.HTTPBadRequest("Bad request", "Not all required fields are provided")
        except WebDriverException:
            bot.driver.quit()
            raise falcon.HTTPBadRequest("Bad request", "There was some issues with Selenium scripts' processes")
        except Exception:
            bot.driver.quit()
            raise falcon.HTTPBadRequest('Bad request', "Something went wrong")

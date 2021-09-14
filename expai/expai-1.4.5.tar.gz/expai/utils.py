import logging


def generate_response(response, to_return_keys=['value']):
    try:
        if response.ok:
            output = {}
            for key in to_return_keys:
                if key in response.json().keys():
                    output[key] = response.json()[key]

            if len(output.keys()) > 0:
                return output
            elif len(output.keys()) == 0 and 'message' in response.json().keys():
                return response.json()['message']
            else:
                return True
        else:
            if 'errors' in response.json().keys():
                logging.error("There was an error. Please, check the details below. \n {}".format(
                    response.json()['errors']))
            else:
                logging.error("There was an error. Please, check the details below. \n {}".format(
                    response.json()['message']))
            return None
    except:
        logging.error("There was an undefined error. Please, try again or contact our support team.")

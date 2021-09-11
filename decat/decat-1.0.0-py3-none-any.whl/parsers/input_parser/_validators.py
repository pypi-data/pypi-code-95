from argparse import ArgumentTypeError


class _AlphaString:

    def __call__(self, input_):
        _err = f'Expected a plain string value without any punctuation, ' \
               f'numeral or special characters, but received: "{input_}"'
        if not(isinstance(input_, str)):
            raise ArgumentTypeError(_err)
        return input_


VALIDATORS = dict(input=_AlphaString())

from battlenet_client.util import localize


def params_headers(function):
    def wrapper(*args, **kwargs):

        kwargs['params'] = {'locale': localize(args[2])}

        if 'headers' not in kwargs.keys():
            kwargs['headers'] = {'Battlenet-Namespace': getattr(args[0], f"{args[3]}")}
        else:
            kwargs['headers']['Battlenet-Namespace'] = getattr(args[0], f"{args[3]}")

        if 'fields' in kwargs.keys():
            kwargs['params'].update({key: value for key, value in kwargs['fields'].items()})
            kwargs.pop('fields', None)

        return function(*args, **kwargs)
    return wrapper

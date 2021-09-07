from collections import defaultdict

from tornado_swagger import _builders
from tornado_swagger._builders import _build_doc_from_func_doc
from tornado_swagger._builders import _format_handler_path
from tornado_swagger._builders import build_swagger_docs
from tornado_swagger import setup

_REST_DOC_CACHE_ = defaultdict(dict)


def _extract_paths(routes):
    import collections
    paths = collections.defaultdict(dict)

    for route in routes:
        for method_name, method_description in _build_doc_from_func_doc(
                route.target
        ).items():
            paths[_format_handler_path(route, method_name)].update(
                {method_name: method_description}
            )

    for rest_path, rest_doc_dict in _REST_DOC_CACHE_.items():
        paths[rest_path].update(rest_doc_dict)

    return paths


def setup_swagger(handlers, app_name, app_description, app_version):
    setattr(_builders, '_extract_paths', _extract_paths)
    setup.setup_swagger(handlers, swagger_url='/swagger-ui',
                        title=f'{app_name} API', description=app_description, api_version=app_version)


def cache_rest_doc(path, method, doc):
    _REST_DOC_CACHE_[path].update({method: build_swagger_docs(doc)})

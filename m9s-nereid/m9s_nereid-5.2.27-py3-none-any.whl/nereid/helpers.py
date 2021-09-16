# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os
import io
import mimetypes
from time import time
from zlib import adler32
import re
import warnings
import unicodedata
from functools import wraps
from hashlib import md5

import trytond.modules
from trytond.transaction import Transaction
from trytond.config import config
from speaklater import is_lazy_string
from flask.helpers import (_PackageBoundObject, locked_cached_property,  # noqa
    get_flashed_messages, flash as _flash, url_for as flask_url_for, safe_join)
from werkzeug.datastructures import Headers
from werkzeug.wsgi import wrap_file
from werkzeug.exceptions import (BadRequest, NotFound,
    RequestedRangeNotSatisfiable, abort)
from werkzeug.utils import redirect
from werkzeug.urls import url_quote
from flask_login import login_required      # noqa

from .globals import (current_app, request, current_locale,  # noqa
        current_website, current_user)


DATABASE_PATH = config.get('database', 'path')


def url_for(endpoint, **values):
    """
    Generates a URL to the given endpoint with the method provided.
    The endpoint is relative to the active module if modules are in use.

    The functionality is documented in `flask.helpers.url_for`

    In addition to the arguments provided by flask, nereid allows the locale
    of the url to be generated to be specified using the locale attribute.
    The default value of locale is the locale of the current request.

    For example::

        url_for('nereid.website.home', locale='en-us')

    """
    if '_secure' in values and '_scheme' not in values:
        warnings.warn(
            "_secure argument will be deprecated in favor of _scheme",
            DeprecationWarning, stacklevel=2
        )
        values['_external'] = True
        values['_scheme'] = 'https'
        values.pop('_secure')

    if 'language' in values:
        warnings.warn(
            "language argument is deprecated in favor of locale",
            DeprecationWarning, stacklevel=2
        )

    # 'static' is Flask's default endpoint for static files.
    # There is no need to set language in URL for static files
    if endpoint != 'static' and \
            'locale' not in values and current_website.locales:
        values['locale'] = current_locale.code

    return flask_url_for(endpoint, **values)


def secure(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not request.is_secure:
            return redirect(request.url.replace('http://', 'https://'))
        else:
            return function(*args, **kwargs)
    return decorated_function



def send_from_directory(directory, filename, **options):
    """
    Send a file from a given directory with :func:`send_file`.  This
    is a secure way to quickly expose static files from an upload folder
    or something similar.

    Example usage::

        @app.route('/uploads/<path:filename>')
        def download_file(filename):
            return send_from_directory(app.config['UPLOAD_FOLDER'],
                                       filename, as_attachment=True)

    .. admonition:: Sending files and Performance

       It is strongly recommended to activate either ``X-Sendfile`` support in
       your webserver or (if no authentication happens) to tell the webserver
       to serve files for the given path on its own without calling into the
       web application for improved performance.

    .. versionadded:: 0.5

    :param directory: the directory where all the files are stored.
    :param filename: the filename relative to that directory to
                     download.
    :param options: optional keyword arguments that are directly
                    forwarded to :func:`send_file`.
    """
    filename = os.fspath(filename)
    directory = os.fspath(directory)
    filename = safe_join(directory, filename)
    if not os.path.isabs(filename):
        #filename = os.path.join(current_app.root_path, filename)
        filename = os.path.join(DATABASE_PATH, current_app.database_name,
            filename)
    try:
        if not os.path.isfile(filename):
            raise NotFound()
    except (TypeError, ValueError):
        raise BadRequest()
    options.setdefault("conditional", True)
    return send_file(filename, **options)


def send_file(filename_or_fp, mimetype=None,
        as_attachment=False, attachment_filename=None,
        add_etags=True, cache_timeout=None, conditional=False,
        last_modified=None):
    """Sends the contents of a file to the client.  This will use the
    most efficient method available and configured.  By default it will
    try to use the WSGI server's file_wrapper support.  Alternatively
    you can set the application's :attr:`~Flask.use_x_sendfile` attribute
    to ``True`` to directly emit an ``X-Sendfile`` header.  This however
    requires support of the underlying webserver for ``X-Sendfile``.

    By default it will try to guess the mimetype for you, but you can
    also explicitly provide one.  For extra security you probably want
    to send certain files as attachment (HTML for instance).  The mimetype
    guessing requires a `filename` or an `attachment_filename` to be
    provided.

    ETags will also be attached automatically if a `filename` is provided. You
    can turn this off by setting `add_etags=False`.

    If `conditional=True` and `filename` is provided, this method will try to
    upgrade the response stream to support range requests.  This will allow
    the request to be answered with partial content response.

    Please never pass filenames to this function from user sources;
    you should use :func:`send_from_directory` instead.

    .. versionadded:: 0.2

    .. versionadded:: 0.5
       The `add_etags`, `cache_timeout` and `conditional` parameters were
       added.  The default behavior is now to attach etags.

    .. versionchanged:: 0.7
       mimetype guessing and etag support for file objects was
       deprecated because it was unreliable.  Pass a filename if you are
       able to, otherwise attach an etag yourself.  This functionality
       will be removed in Flask 1.0

    .. versionchanged:: 0.9
       cache_timeout pulls its default from application config, when None.

    .. versionchanged:: 0.12
       The filename is no longer automatically inferred from file objects. If
       you want to use automatic mimetype and etag support, pass a filepath via
       `filename_or_fp` or `attachment_filename`.

    .. versionchanged:: 0.12
       The `attachment_filename` is preferred over `filename` for MIME-type
       detection.

    .. versionchanged:: 1.0
        UTF-8 filenames, as specified in `RFC 2231`_, are supported.

    .. _RFC 2231: https://tools.ietf.org/html/rfc2231#section-4

    .. versionchanged:: 1.0.3
        Filenames are encoded with ASCII instead of Latin-1 for broader
        compatibility with WSGI servers.

    .. versionchanged:: 1.1
        Filename may be a :class:`~os.PathLike` object.

    .. versionadded:: 1.1
        Partial content supports :class:`~io.BytesIO`.

    :param filename_or_fp: the filename of the file to send.
                           This is relative to the :attr:`~nereid.root_path`
                           if a relative path is specified.
                           Alternatively a file object might be provided in
                           which case ``X-Sendfile`` might not work and fall
                           back to the traditional method.  Make sure that the
                           file pointer is positioned at the start of data to
                           send before calling :func:`send_file`.
    :param mimetype: the mimetype of the file if provided. If a file path is
                     given, auto detection happens as fallback, otherwise an
                     error will be raised.
    :param as_attachment: set to ``True`` if you want to send this file with
                          a ``Content-Disposition: attachment`` header.
    :param attachment_filename: the filename for the attachment if it
                                differs from the file's filename.
    :param add_etags: set to ``False`` to disable attaching of etags.
    :param conditional: set to ``True`` to enable conditional responses.

    :param cache_timeout: the timeout in seconds for the headers. When ``None``
                          (default), this value is set by
                          :meth:`~Flask.get_send_file_max_age` of
                          :data:`~flask.current_app`.
    :param last_modified: set the ``Last-Modified`` header to this value,
        a :class:`~datetime.datetime` or timestamp.
        If a file was passed, this overrides its mtime.
    """
    mtime = None
    fsize = None

    if hasattr(filename_or_fp, "__fspath__"):
        filename_or_fp = os.fspath(filename_or_fp)

    if isinstance(filename_or_fp, str):
        filename = filename_or_fp
        if not os.path.isabs(filename):
            #filename = os.path.join(current_app.root_path, filename)
            filename = os.path.join(DATABASE_PATH, current_app.database_name,
                filename)
        file = None
        if attachment_filename is None:
            attachment_filename = os.path.basename(filename)
    else:
        file = filename_or_fp
        filename = None

    if mimetype is None:
        if attachment_filename is not None:
            mimetype = (
                mimetypes.guess_type(attachment_filename)[0]
                or "application/octet-stream"
            )

        if mimetype is None:
            raise ValueError(
                "Unable to infer MIME-type because no filename is available. "
                "Please set either `attachment_filename`, pass a filepath to "
                "`filename_or_fp` or set your own MIME-type via `mimetype`."
            )

    headers = Headers()
    if as_attachment:
        if attachment_filename is None:
            raise TypeError(
                "filename unavailable, required for sending as attachment")

        if not isinstance(attachment_filename, str):
            attachment_filename = attachment_filename.decode("utf-8")

        try:
            attachment_filename = attachment_filename.encode("ascii")
        except UnicodeEncodeError:
            filenames = {
                "filename": unicodedata.normalize(
                    "NFKD", attachment_filename).encode(
                    "ascii", "ignore"
                ),
                "filename*": "UTF-8''%s" % url_quote(
                    attachment_filename, safe=b""),
            }
        else:
            filenames = {"filename": attachment_filename}

        headers.add("Content-Disposition", "attachment", **filenames)

    if current_app.use_x_sendfile and filename:
        if file is not None:
            file.close()
        headers["X-Sendfile"] = filename
        fsize = os.path.getsize(filename)
        headers["Content-Length"] = fsize
        data = None
    else:
        if file is None:
            file = open(filename, "rb")
            mtime = os.path.getmtime(filename)
            fsize = os.path.getsize(filename)
            headers["Content-Length"] = fsize
        elif isinstance(file, io.BytesIO):
            try:
                fsize = file.getbuffer().nbytes
            except AttributeError:
                # Python 2 doesn't have getbuffer
                fsize = len(file.getvalue())
            headers["Content-Length"] = fsize
        data = wrap_file(request.environ, file)

    rv = current_app.response_class(
        data, mimetype=mimetype, headers=headers, direct_passthrough=True
    )

    if last_modified is not None:
        rv.last_modified = last_modified
    elif mtime is not None:
        rv.last_modified = mtime

    rv.cache_control.public = True
    if cache_timeout is None:
        cache_timeout = current_app.get_send_file_max_age(filename)
    if cache_timeout is not None:
        rv.cache_control.max_age = cache_timeout
        rv.expires = int(time() + cache_timeout)

    if add_etags and filename is not None:
        from warnings import warn

        try:
            rv.set_etag(
                "nereid-%s-%s-%s"
                % (
                    os.path.getmtime(filename),
                    os.path.getsize(filename),
                    adler32(
                        filename.encode("utf-8")
                        if isinstance(filename, str)
                        else filename
                    )
                    & 0xFFFFFFFF,
                )
            )
        except OSError:
            warn(
                "Access %s failed, maybe it does not exist, so ignore etags in "
                "headers" % filename,
                stacklevel=2,
            )

    if conditional:
        try:
            rv = rv.make_conditional(request, accept_ranges=True,
                complete_length=fsize)
        except RequestedRangeNotSatisfiable:
            if file is not None:
                file.close()
            raise
        # make sure we don't send x-sendfile for servers that
        # ignore the 304 status code for x-sendfile.
        if rv.status_code == 304:
            rv.headers.pop("x-sendfile", None)
    return rv


# The slugify method from nereid went upstream into 5.4
# Only difference: we want lower case on slugs
# TODO: Extend on 5.4 to that from trytond/tools/misc
_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(value, hyphenate='-'):
    if not isinstance(value, str):
        value = str(value)
    value = unicodedata.normalize('NFKD', value)
    value = str(_slugify_strip_re.sub('', value).strip())
    return _slugify_hyphenate_re.sub(hyphenate, value).lower()


def _rst_to_html_filter(value):
    """
    Converts RST text to HTML
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    This uses docutils, if the library is missing, then the
    original text is returned

    Loading to environment::
             from jinja2 import Environment
             env = Environment()
             env.filters['rst'] = rst_to_html
             template = env.from_string("Welcome {{name|rst}}")
             template.render(name="**Sharoon**")
    """
    try:
        from docutils import core
        parts = core.publish_parts(source=value, writer_name='html')
        return parts['body_pre_docinfo'] + parts['fragment']
    except Exception:
        return value


def key_from_list(list_of_args):
    """
    Builds a key from a list of arguments which could be used for caching
    The key s constructed as an md5 hash
    """
    hash = md5()
    hash.update(repr(list_of_args).encode('utf-8'))
    return hash.hexdigest()


def get_website_from_host(http_host):
    """Try to find the website name from the HTTP_HOST name"""
    return http_host.split(':')[0]


def make_crumbs(browse_record, endpoint, add_home=True, max_depth=10,
                field_map_changes=None, root_ids=None):
    """
    Makes bread crumbs for a given browse record based on the field
    parent of the browse record

    :param browse_record: The browse record of the object from which upward
                          tracing of crumbs need to be done
    :param endpoint: The endpoint against which the urls have to be generated
    :param add_home: If provided will add home and home url as the first item
    :param max_depth: Maximum depth of the crumbs
    :param field_map_changes: A dictionary/list of key value pair (tuples) to
                              update the default field_map. Only the changing
                              entries need to be provided.
    :param root_ids: IDs of root nodes where the recursion to a parent node
                     will need to be stopped. If not specified the recursion
                     continues upto the max_depth. Expects a list or tuple of
                     ids.

    .. versionchanged:: 0.3
        Added root_ids
    """
    field_map = dict(
        parent_field='parent',
        uri_field='uri',
        title_field='title',
    )
    if field_map_changes is not None:
        field_map.update(field_map_changes)
    if root_ids is None:
        root_ids = tuple()

    def recurse(node, level=1):
        if level > max_depth or not node:
            return []
        data_pair = (
            url_for(endpoint, uri=getattr(node, field_map['uri_field'])),
            getattr(node, field_map['title_field'])
        )
        if node.id in root_ids:
            return [data_pair]
        else:
            return [data_pair] + recurse(
                getattr(node, field_map['parent_field']), level + 1
            )

    items = recurse(browse_record)

    if add_home:
        items.append((url_for('nereid.website.home'), 'Home'))

    # The bread crumb is now in reverse order with home at end, reverse it
    items.reverse()

    return items


def root_transaction_if_required(function):
    """
    Starts a root transaction if one is not there. This behavior is used when
    run from tests cases which manage the transaction on its own.
    """
    @wraps(function)
    def decorated_function(self, *args, **kwargs):

        transaction = None
        if Transaction().connection is None:
            # Start transaction since connection is None
            transaction = Transaction().start(
                self.database_name, 0, readonly=True
            )
        try:
            return function(self, *args, **kwargs)
        finally:
            if transaction is not None:
                # TODO: Find some better way close transaction
                transaction.__exit__(None, None, None)

    return decorated_function


def flash(message, category='message'):
    """
    Lazy strings are no real strings so pickling them results in strange issues.
    Pickling cannot be avoided because of the way sessions work. Hence, this
    special flash function converts lazy strings to unicode content.

    .. versionadded:: 3.0.4.1

    :param message: the message to be flashed.
    :param category: the category for the message.  The following values
                     are recommended: ``'message'`` for any kind of message,
                     ``'error'`` for errors, ``'info'`` for information
                     messages and ``'warning'`` for warnings.  However any
                     kind of string can be used as category.
    """
    if is_lazy_string(message):
        message = str(message)
    return _flash(message, category)


def route(rule, **options):
    """Like :meth:`Flask.route` but for nereid.

    .. versionadded:: 3.0.7.0

    Unlike the implementation in flask and flask.blueprint route decorator does
    not require an existing nereid application or a blueprint instance. Instead
    the decorator adds an attribute to the method called `_url_rules`.

    .. code-block:: python
        :emphasize-lines: 1,7

        from nereid import route

        class Product:
            __name__ = 'product.product'

            @classmethod
            @route('/product/<uri>')
            def render_product(cls, uri):
                ...
                return 'Product Information'

    """
    def decorator(f):
        if not hasattr(f, '_url_rules'):
            f._url_rules = []
        f._url_rules.append((rule, options))
        return f
    return decorator


def get_version():
    """
    Return the version of nereid by looking up the version as read by the
    tryton module loader.
    """
    return trytond.modules.get_module_info('nereid')['version']


def context_processor(name=None):
    """Makes method available in template context. By default method will be
    registered by its name.

    Decorator adds an attribute to the method called `_context_processor`.

    .. code-block:: python
        :emphasize-lines: 1,7

        from nereid import context_processor

        class Product:
            __name__ = 'product.product'

            @classmethod
            @context_processor('get_sale_price')
            def get_sale_price(cls):
                ...
                return 'Product sale price'
    """
    def decorator(f):
        f._context_processor = True
        if name is not None:
            f.__name__ = name
        return f
    return decorator


def template_filter(name=None):
    """
    If you want to register your own filters in Jinja2 you have two ways to do
    that. You can either put them by hand into the jinja_env of the application
    or use the template_filter() decorator.

    The two following examples work the same and both reverse an object::

        from nereid import template_filter

        class MyModel:
            __name__ = 'product.product'

            @classmethod
            @template_filter('reverse')
            def reverse_filter(cls, s):
                return s[::-1]

    Alternatively you can inject it into the jinja environment in your
    `application.py`::

        def reverse_filter(s):
            return s[::-1]
        app.jinja_env.filters['reverse'] = reverse_filter

    In case of the decorator the argument is optional if you want to use the
    function name as name of the filter. Once registered, you can use the
    filter in your templates in the same way as Jinja2’s builtin filters, for
    example if you have a Python list in context called mylist::

        {% for x in mylist | reverse %}
        {% endfor %}
    """
    def decorator(f):
        f._template_filter = True
        if name is not None:
            f.__name__ = name
        return f
    return decorator

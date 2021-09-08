"""
Module to read and parse YAML or JSON files, locally or remotely (gitlab only)

 jsonref with YAML reading added.

 copied directly from jsonref v0.2, with added routines _yaml_load
 and _yaml_loads replacing json.load and json.loads
 Added/modified lines are marked "# WCC"
"""

import functools
import os
import json
import yaml # WCC
import operator
import re
import sys
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
import copy
from json.decoder import JSONDecodeError
from pathlib import Path
from urllib import parse as urlparse
from urllib.parse import unquote
from urllib.request import urlopen
import logging
logger = logging.getLogger("obsinfo")
from ..misc.configuration import ObsinfoConfiguration

#obsinfo imports
from ..misc.remoteGitLab import gitLabFile

from ..misc.discoveryfiles import Datapath

try:
    from collections.abc import Mapping, MutableMapping, Sequence
except ImportError:
    from collections import Mapping, MutableMapping, Sequence
    


PY3 = sys.version_info[0] >= 3


unicode = str
basestring = str
iteritems = operator.methodcaller("items")

try:
    # If requests >=1.0 is available, we will use it
    import requests

    if not callable(requests.Response.json):
        requests = None
except ImportError:
    requests = None

from proxytypes import LazyProxy, Proxy

__version__ = "0.2"



class JsonRefError(Exception):
    """
    Create exception for JSONRef
    
      **Attributes:**
     
    
        * message (str): message to print with exception
        * reference (str): reference where exception occurred
        * uri (str or path-like): uri of file being processed 
        * base_uri: (str or path-like): base_uri (complement) of file being processed
        * path = list of string keywords: keywords of different $ref in lists or dictionaries
        * cause (str): cause of exception
      
    """
    
    def __init__(self, message, reference, uri="", base_uri="", path=(), cause=None):
        self.message = message
        self.reference = reference
        self.uri = uri
        self.base_uri = base_uri
        self.path = list(path)
        self.cause = self.__cause__ = cause

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.message)

    def __str__(self):
        return str(self.message)


class JsonRef(LazyProxy):
    """
    A lazy loading proxy to the dereferenced data pointed to by a JSON
    Reference object.
    
      **Attributes:**
     
    
        * __reference__: dictionary object referenced to by a ``$ref``
        * base_uri: object of type :class:`Path` which is used to build the full uri
        * loader:  a loader object (a callable) such as :class:`JsonLoader` , to load a JSON or YAML file/string
        * jsonschema = Flag to turn on ``JSON Schema`` mode
        * load_on_repr = If set to ``False``, :func:`repr` call on a
                :class:`JsonRef` object will not cause the reference to be loaded
                if it hasn't already. (defaults to ``True``)
        * path = list of string keywords: keywords of different $ref in lists or dictionaries
        * store = dictionary of cached objects used to prevent reading files over again
        * datapath = object of :class:`Datapath`, stores directories to search for files
        
    """

    __notproxied__ = ("__reference__",)

    @classmethod
    def replace_refs(cls, obj, _recursive=False, **kwargs):
        """
        Returns a deep copy of ``obj`` with all contained JSON reference objects
        replaced with :class:`JsonRef` instances.

        :param obj: If this is a JSON reference object, a :class:`JsonRef`
            instance will be created. If ``obj`` is not a JSON reference object,
            a deep copy of it will be created with all contained JSON
            reference objects replaced by :class:`JsonRef` instances
        :type obj: Either JSONref or collection object
        :param recursive: Processes ``$ref`` recursively
        :type recursive: boolean
        :param kwargs:  Keyword arguments passed to :func:`json.loads`
        :type kwargs: dict
        :returns: object of :class:`JsonRef` containing the information in ``$ref`` file
        :raises: TypeError, ValueError through JsonRef object creation

        
        ``kwargs`` include:
            :param base_uri:  URI to resolve relative references against. 
                Can be remote (https://) or local(file://) 
                This is how datapath is implemented
            :type base_uri: object of type :class:`Path`
            :param datapath:  object to implement file discovery in a list of directories
            :type base_uri: object of type :class:`Datapath`
            :param loader: Callable that takes a URI and returns the parsed JSON
                (defaults to global ``jsonloader``, a :class:`JsonLoader` instance)
            :type loader: a loader object such as :class:`JsonLoader` 
            :param jsonschema: Flag to turn on `JSON Schema mode <http://json-schema.org/latest/json-schema-core.html#anchor25>`_,
                which means the file is a schema file.
                This makes 'id' keyword to change the ``base_uri`` for references contained within
                the object, such as $ref: '#/definitions' 
            :type jsonschema: boolean
            :param load_on_repr: If set to ``False``, :func:`repr` call on a
                :class:`JsonRef` object will not cause the reference to be loaded
                if it hasn't already. (defaults to ``True``)
            :type load_on_repr: boolean
        
        """
               
        store = kwargs.setdefault("_store", _URIDict())
        base_uri, frag = urlparse.urldefrag(kwargs.get("base_uri", ""))
        
        store_uri = None  # If this does not get set, we won't store the result
        if not frag and not _recursive:
            store_uri = base_uri
        try:
            if kwargs.get("jsonschema") and isinstance(obj["id"], basestring): # It's a schema
                kwargs["base_uri"] = urlparse.urljoin( 
                    kwargs.get("base_uri", ""), obj["id"]
                )
                store_uri = kwargs["base_uri"]
        except (TypeError, LookupError):
            pass

        try:
            if not isinstance(obj["$ref"], basestring): #It's a $ref but not a string
                raise TypeError # This is a dirty trick to skip the else: clause
        except (TypeError, LookupError):
            pass
        else:
            return cls(obj, **kwargs) #__init__ and Return JsonRef object (content of $ref) if a string

        # If our obj was not a json reference object, iterate through it,
        # replacing children with JsonRefs
        kwargs["_recursive"] = True
        path = list(kwargs.pop("_path", ()))
        if isinstance(obj, Mapping):
            obj = type(obj)( #Calls __init__ for the relevant object type
                (k, cls.replace_refs(v, _path=path + [k], **kwargs))
                for k, v in iteritems(obj)
            )
        elif isinstance(obj, Sequence) and not isinstance(obj, basestring):
            obj = type(obj)( #Calls __init__ for the relevant object type
                cls.replace_refs(v, _path=path + [i], **kwargs)
                for i, v in enumerate(obj)
            )
        #else obj is a "leaf" object (not a list, not a directory) and thus not replaceable, we simply return it
        
        if store_uri is not None:
            store[store_uri] = obj
            
        return obj

    def __init__(
        self,
        refobj,
        base_uri="",
        loader=None,
        jsonschema=False,
        load_on_repr=True,
        _path=(),
        _store=None,
        datapath=None,
    ):
        if not isinstance(refobj.get("$ref"), basestring):
            msg = f'Not a valid json reference object'
            logger.error(msg)
            raise ValueError(msg)

        self.__reference__ = refobj
        self.base_uri = base_uri 
        self.loader = loader or jsonloader
        self.jsonschema = jsonschema
        self.load_on_repr = load_on_repr
        self.path = list(_path)
        self.store = _store  # Use the same object to be shared with children
        self.datapath = datapath
        if self.store is None:
            self.store = _URIDict()

    @property
    def _ref_kwargs(self):
        return dict(
            base_uri=self.base_uri,
            loader=self.loader,
            jsonschema=self.jsonschema,
            load_on_repr=self.load_on_repr,
            _path=self.path,
            _store=self.store,
            datapath = self.datapath,
        )

    @property
    def full_uri(self):
        """
        This method/property returns the full uri to reference a ``$ref`` object.
        It's the heart of how a datapath is used to either access a local or remote (gitlab) file.
        All schema files are supposed to be local, part of the obsinfo distribution
        
        :returns: updated full uri
        :raises: ValueError
        """
        
        kwargs = self._ref_kwargs
        
        if kwargs['jsonschema']:
            return urlparse.urljoin(self.base_uri, self.__reference__["$ref"]) 
        else:        
            dp = kwargs["datapath"]
            if not dp:
                msg = f'Error in datapath in full_uri, reference: {self.__reference__["$ref"]}'
                logger.error(msg)
                raise ValueError(msg)
            base_uri = Path(dp.build_datapath(self.__reference__["$ref"]))
            
            tupl = urlparse.urlsplit(str(base_uri))
            path = unquote(tupl.path)
            frag = tupl.fragment
            new_uri = Datapath.add_frag(path, frag)
            # define the uri depending on whether it is remote or not
            self.base_uri =  new_uri if gitLabFile.isRemote(str(base_uri)) else\
                            unquote(base_uri.as_uri())
            
            return(self.base_uri) 
    
        
    def callback(self):
        """
        Callback from proxytypes, :class:`LazyProxy`. 
        
        Resolves the pointer (part of the dictionary read from the info file)
        that is incorporated instead of ``$ref``. Updates ``base_uri``
        
        :returns: the fragment portion of the base_doc, which has already had its ``$ref`` replaced. 
        """
        uri, fragment = urlparse.urldefrag(self.full_uri)
        # If we already looked this up, return a reference to the same object
        if uri in self.store:
            result = self.resolve_pointer(self.store[uri], fragment)
        else:
            # Remote ref
            try:              
                base_doc = self.loader(uri)
            except Exception as e:
                # self._error("%s: %s" % (e.__class__.__name__, unicode(e)), cause=e)
                # WCC
                msg = f"Exception in JSONRef callback {e}"
                print(msg)
                logger.error(msg)
                return None
                
            kwargs = self._ref_kwargs
            kwargs["base_uri"] = uri 
            base_doc = JsonRef.replace_refs(base_doc, **kwargs)
            result = self.resolve_pointer(base_doc, fragment)
            
        if hasattr(result, "__subject__"):
            # TODO: Circular ref detection
            result = result.__subject__
        return result

    def resolve_pointer(self, document, pointer):
        """
        Resolve a json pointer ``pointer`` within the referenced ``document``.

        :argument document: the referent document
        :argument str pointer: a json pointer URI fragment to resolve within it
        
        :returns: part of document dictionary pointed at by pointer

        """
        
        
        # Do only split at single forward slashes which are not prefixed by a caret
        parts = re.split(r"(?<!\^)/", unquote(pointer.lstrip("/"))) if pointer else []
       
        for part in parts:
            # Restore escaped slashes and carets
            replacements = {r"^/": r"/", r"^^": r"^"}
            part = re.sub(
                "|".join(re.escape(key) for key in replacements.keys()),
                lambda k: replacements[k.group(0)],
                part,
            )
            if isinstance(document, Sequence):
                # Try to turn an array index to an int
                try:
                    part = int(part)
                except ValueError:
                    pass
            try:
                document = document[part]
            except (TypeError, LookupError) as e:
                self._error("Unresolvable JSON pointer: %r" % pointer, cause=e)
        return document

    def _error(self, message, cause=None):
        msg = f"Error {message} in {self.__reference_}: {cause}"
        logger.error(msg)
        raise JsonRefError(
            message,
            self.__reference__,
            uri=self.full_uri,
            base_uri=self.base_uri,
            path=self.path,
            cause=cause,
        )

    def __repr__(self):
        if hasattr(self, "cache") or self.load_on_repr:
            return repr(self.__subject__)
        return "JsonRef(%r)" % self.__reference__


class _URIDict(MutableMapping):
    """
    Dictionary which uses normalized URIs as keys.
    
    Used to cache already read ``$ref``
    
      **Attributes:**
     
    
        * store: dictionary of cached objects used to prevent reading files over again

    """

    def normalize(self, uri):
        """
        Return URL from an uri
        :param uri: uri to be normalized
        :type uri: pathlike or str object
        :returns: URL as pathlike object
        
        """
        return urlparse.urlsplit(uri).geturl()

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.store.update(*args, **kwargs)

    def __getitem__(self, uri):
        return self.store[self.normalize(uri)]

    def __setitem__(self, uri, value):
        self.store[self.normalize(uri)] = value

    def __delitem__(self, uri):
        del self.store[self.normalize(uri)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return repr(self.store)


class JsonLoader(object):
    """
    Provides a callable which takes a URI, and returns the loaded JSON referred
    to by that URI. Uses :mod:`requests` if available for HTTP URIs, and falls
    back to :mod:`urllib`. By default it keeps a cache of previously loaded
    documents.

      **Attributes:**
     
    
        * store: pre-populated dictionary matching URIs to loaded JSON
            documents used as cache
        * cache_results (boolean): if this is set to false, the internal cache of
        * loaded JSON documents is not used
        
    """

    def __init__(self, store=(), cache_results=True):
        self.store = _URIDict(store)
        self.cache_results = cache_results

    def __call__(self, uri, **kwargs):
        """
        Return the loaded JSON or YAML referred to by ``uri``

        :param uri: The URI of the JSON or YAML document to load
        :type uri: path-like object, string or byte string
        :param kwargs: Keyword arguments passed to :func:`json.loads
        :type kwargs: dict
        :returns: dictionary of parsed YAML or JSON formats
         
        """
        if uri in self.store:
            return self.store[uri]
        else:
            result = self.get_json_or_yaml(uri, **kwargs)
            if self.cache_results:
                self.store[uri] = result
            return result

    def get_json_or_yaml(self, uri, **kwargs):
        """
        Open either a local file, if uri scheme is ``file`` or a remote one, calling a gitlab method
        which implements the gitlab API (version 4)
        
        :param uri: The URI of the JSON or YAML document to load
        :type uri: path-like object, string or byte string
        :param kwargs: Keyword arguments passed to :func:`json.loads`
        :type kwargs: dict
        :returns: dictionary of parsed YAML or JSON formats
        :raises: FileNotFoundError, IOError, OSError
        
        """
        scheme = urlparse.urlsplit(uri).scheme
        path = urlparse.urlsplit(uri).path

        logger.info(f"Opening file: {path}")
        # Open locally or remotely according to scheme 
        if scheme == 'file':
            try:
                with open(path, "rt") as fp:
                    strm = fp.read()
            except FileNotFoundError:
                msg = f'File not found: {path}'
                logger.error(msg)
                raise FileNotFoundError(msg)
            except (IOError, OSError):
                msg = f'Input/Output error with file: {path}'
                print(msg)
                logger.error(msg)
                raise
        else:
            strm = gitLabFile.get_gitlab_file(uri)
          
        result = _yaml_loads(strm, **kwargs)   # LFA
        
        return result


jsonloader = JsonLoader()


def load(fp, base_uri="", loader=None, jsonschema=False, load_on_repr=True, datapath=None,
         **kwargs):
    """
    Drop in replacement for :func:`json.load`, where JSON references are
    proxied to their referent data.
    
    The difference between load and loads is that the first uses a file-like object and
    the second a string.

    :param fp: File-like object containing JSON document
    :type fp: File-like object
    :param base_uri:  URI to resolve relative references against. Can be remote (https://) or local(file://)  This is how datapath is implemented
    :type base_uri: object of type :class:`Path`
    :param datapath:  object to implement file discovery in a list of directories
    :type datapath: object of type :class:`Datapath`
    :param loader: Callable that takes a URI and returns the parsed JSON (defaults to global ``jsonloader``, a :class:`JsonLoader` instance)
    :type loader: a loader object such as :class:`JsonLoader` 
    :param jsonschema: Flag to turn on `JSON Schema mode <http://json-schema.org/latest/json-schema-core.html#anchor25>`_, which means the file is a schema file. This makes 'id' keyword to change the ``base_uri`` for references contained within the object, such as $ref: '#/definitions' 
    :type jsonschema: boolean
    :param load_on_repr: If set to ``False``, :func:`repr` call on a:class:`JsonRef` object will not cause the reference to be loaded if it hasn't already. (defaults to ``True``)
    :type load_on_repr: boolean
    :param kwargs: This function takes any of the keyword arguments from :meth:`JsonRef.replace_refs`. Any other keyword arguments will be passed to :func:`_yaml_load`
    :type kwargs: dict
    :returns: dictionary of parsed YAML or JSON formats
    
    """
    
    # Assign a default loader, jsonloader.
    if loader is None:
        loader = functools.partial(jsonloader, **kwargs)
    
    # Convert encoded characters
    base_uri = unquote(base_uri)
    
    
    return JsonRef.replace_refs(
        _yaml_load(fp, **kwargs), # WCC
        base_uri=base_uri,
        loader=loader,
        jsonschema=jsonschema,
        load_on_repr=load_on_repr,
        datapath=datapath, #LFA. Datapath is the list of paths where files can potentialy be found
    )


def loads(s, base_uri="", loader=None, jsonschema=False, 
          load_on_repr=True, datapath=None, recursive=True, **kwargs):
    """
    Drop in replacement for :func:`json.loads`, where JSON references are
    proxied to their referent data.

    The difference between load and loads is that the first uses a file-like object and
    the second a string.

    :param s: String containing JSON document
    :type s: str
    :param base_uri:  URI to resolve relative references against. Can be remote (https://) or local(file://)  This is how datapath is implemented
    :type base_uri: object of type :class:`Path`
    :param datapath:  object to implement file discovery in a list of directories
    :type datapath: object of type :class:`Datapath`
    :param loader: Callable that takes a URI and returns the parsed JSON (defaults to global ``jsonloader``, a :class:`JsonLoader` instance)
    :type loader: a loader object such as :class:`JsonLoader` 
    :param jsonschema: Flag to turn on `JSON Schema mode <http://json-schema.org/latest/json-schema-core.html#anchor25>`_, which means the file is a schema file. This makes 'id' keyword to change the ``base_uri`` for references contained within the object, such as $ref: '#/definitions' 
    :type jsonschema: boolean
    :param load_on_repr: If set to ``False``, :func:`repr` call on a:class:`JsonRef` object will not cause the reference to be loaded if it hasn't already. (defaults to ``True``)
    :type load_on_repr: boolean
    :param kwargs: This function takes any of the keyword arguments from :meth:`JsonRef.replace_refs`. Any other keyword arguments will be passed to :func:`_yaml_load`
    :type kwargs: dict
    :returns: dictionary of decoded JSON or YAML 

    """
    
    
    if loader is None:
        loader = functools.partial(jsonloader, **kwargs)
    
    dic = _yaml_loads(s, **kwargs) if isinstance(s, str) else s
        
    if recursive:
        return JsonRef.replace_refs(
            dic,  # WCC et LFA
            base_uri=base_uri,
            loader=loader,
            jsonschema=jsonschema,
            load_on_repr=load_on_repr,
            datapath=datapath,
        )
    else:
        return dic


def load_uri(uri, base_uri=None, loader=None, jsonschema=False, load_on_repr=True):
    """
    Load JSON data from ``uri`` instead of file-like object or string.
     with JSON references proxied to their referent data. Not used in obsinfo.

    :param uri: URI to fetch the JSON from
    :type uri: string or path-like object
    :param base_uri:  URI to resolve relative references against. Can be remote (https://) or local(file://)  This is how datapath is implemented
    :type base_uri: object of type :class:`Path`
    :param datapath:  object to implement file discovery in a list of directories
    :type datapath: object of type :class:`Datapath`
    :param loader: Callable that takes a URI and returns the parsed JSON (defaults to global ``jsonloader``, a :class:`JsonLoader` instance)
    :type loader: a loader object such as :class:`JsonLoader` 
    :param jsonschema: Flag to turn on `JSON Schema mode <http://json-schema.org/latest/json-schema-core.html#anchor25>`_, which means the file is a schema file. This makes 'id' keyword to change the ``base_uri`` for references contained within the object, such as $ref: '#/definitions' 
    :type jsonschema: boolean
    :param load_on_repr: If set to ``False``, :func:`repr` call on a:class:`JsonRef` object will not cause the reference to be loaded if it hasn't already. (defaults to ``True``)
    :type load_on_repr: boolean
    :returns: dictionary of parsed YAML or JSON formats
    """

    if loader is None:
        loader = jsonloader
    if base_uri is None: 
        base_uri = uri

    return JsonRef.replace_refs(
        loader(uri),
        base_uri=base_uri,
        loader=loader,
        jsonschema=jsonschema,
        load_on_repr=load_on_repr,
        datapath=datapath,
    )

# WCC ADDED BEGIN
# Method read_json_yaml_ref  in ObsMetadata uses load, not loads. Load loads a file.
def _yaml_load(fp, **kwargs):
    """ 
    Call {yaml,json}.load according to file type. Invoked by 
       :func: load
    
    :param fp: File-like object containing JSON document
    :type fp: File-like object
    :param kwargs: This function takes any of the keyword arguments from
        :meth:`JsonRef.replace_refs`. Any other keyword arguments will be passed to 
        :func:`_yaml_loads`
    :type kwargs: dict
    :returns: dictionary of parsed YAML or JSON formats
    :raises: JSONDecodeError

    """
    
    try:
        return json.load(fp, **kwargs)
    # except JSONDecodeError:
    except:
        fp.seek(0)
        try:
            return yaml.safe_load(fp)
        # except ScannerError:
        except:
            msg = f'file {fp.name} is neither JSON nor YAML.'
            print(msg)
            logger.error(msg)                                 
            raise JSONDecodeError(msg, fp.name, 0)
    return None

# Method validate in ObsMetadata uses loads, not load. loads loads a string, not a file.
def _yaml_loads(s, **kwargs):
    """ 
    Call {yaml,json}.loads according to file type. Invoked by 
       :func: loads 
    
    :param s: String containing JSON document
    The difference between load and loads is that the first uses a file-like object and
    the second a string.
    :type s: str
    :param kwargs: This function takes any of the keyword arguments from
        :meth:`JsonRef.replace_refs`. Any other keyword arguments will be passed to 
        :func:`_yaml_loads`
    :type kwargs: dict
    :returns: dictionary of parsed YAML or JSON formats
    :raises: JSONDecodeError
    """
    a = None
    
    kw = copy.deepcopy(kwargs) #copy to make sure you don alter the original kwargs
    kw.pop('base_uri', None)
    kw.pop('datapath', None)
    
    if s[:3] == '---':
        try:
            a = yaml.safe_load(s, **kw)
        except:
            try:
                a = json.loads(s, **kwargs)
            except:
                msg = f'String is neither JSON nor YAML'
                logger.error(msg)
                raise JSONDecodeError(msg)
      
    else:
        try:
            a = json.loads(s, **kwargs)
        except:
            try:
                a = yaml.safe_load(s, **kwargs)
            except:
                msg = f'String is neither JSON nor YAML'
                logger.error(msg)
                raise JSONDecodeError(msg)
                          
    return a

# WCC ADDED END

def dump(obj, fp, **kwargs):
    """
    Serialize ``obj``, which may contain :class:`JsonRef` objects, as a JSON
    formatted stream to file-like ``fp``. ``JsonRef`` objects will be dumped as the
    original reference object they were created from.

    :param obj: Object to serialize
    :type obj: object
    :param fp: File-like object that will be used to dump obj
    :type fp: file-like object
    :param kwargs: Keyword arguments are the same as to 
      :func:`json.dump`
    :type kwargs: dict
    """
    # Strangely, json.dumps does not use the custom serialization from our
    # encoder on python 2.7+. Instead just write json.dumps output to a file.
    fp.write(dumps(obj, **kwargs))


def dumps(obj, **kwargs):
    """
    Serialize ``obj``, which may contain :class:`JsonRef` objects, to a JSON
    formatted string. ``JsonRef`` objects will be dumped as the original
    reference object they were created from.

    :param obj: Object to serialize
    :type obj: object
    :param kwargs: Keyword arguments are the same as to 
      :func:`json.dump`
    :type kwargs: dict
    :returns: dumped string
    """
    
    kwargs["cls"] = _ref_encoder_factory(kwargs.get("cls", json.JSONEncoder))
    return json.dumps(obj, **kwargs)


def _ref_encoder_factory(cls):
    """
    Encode object of class cls
    
    :param cls: class to encode object with
    :type cls: class
    :returns: encoded object
    
    """

    class JSONRefEncoder(cls):
        """
        Methods to encode an object of class cls, according to Python version
        
        Methods:
        ----------
          :members:
          
        """
        def default(self, o):
            if hasattr(o, "__reference__"):
                return o.__reference__
            return super(JSONRefEncoder, cls).default(o)

        # Python 2.6 doesn't work with the default method
        def _iterencode(self, o, *args, **kwargs):
            if hasattr(o, "__reference__"):
                o = o.__reference__
            return super(JSONRefEncoder, self)._iterencode(o, *args, **kwargs)

        # Pypy doesn't work with either of the other methods
        def _encode(self, o, *args, **kwargs):
            if hasattr(o, "__reference__"):
                o = o.__reference__
            return super(JSONRefEncoder, self)._encode(o, *args, **kwargs)

    return JSONRefEncoder

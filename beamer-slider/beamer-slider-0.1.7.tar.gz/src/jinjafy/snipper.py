from jinja2 import nodes
from jinja2.ext import Extension
import os


class SnipperExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['snipper'])

    def __init__(self, environment):
        super(SnipperExtension, self).__init__(environment)

        # add the defaults to the environment
        environment.extend(
            fragment_cache_prefix='',
            fragment_cache=None
        )
        self.ofile = ""

    def parse(self, parser):
        # the first token is the token that started the tag.  In our case
        # we only listen to ``'cache'`` so this will be a name token with
        # `cache` as value.  We get the line number so that we can give
        # that line number to the nodes we create by hand.
        lineno = next(parser.stream).lineno

        # now we parse a single expression that is used as cache key.
        args = [parser.parse_expression()]
        ofile = os.path.join(os.path.dirname(parser.filename), args[0].value)
        args[0].value = ofile
        if not os.path.isdir(os.path.dirname(ofile)):
            os.makedirs(os.path.dirname(ofile))
        self.ofile = ofile
        print("Snipper args", args, "ofile", ofile)

        # if there is a comma, the user provided a timeout.  If not use
        # None as second parameter.
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        # now we parse the body of the cache block up to `endcache` and
        # drop the needle (which would always be `endcache` in that case)
        body = parser.parse_statements(['name:endsnipper'], drop_needle=True)

        # now return a `CallBlock` node that calls our _cache_support
        # helper method on this extension.
        return nodes.CallBlock(self.call_method('_snip_method', args),
                                [], [], body).set_lineno(lineno)

        # parser.environment.loader.searchpath
        # parser.parse_statements(body)
        return body

    def _snip_method(self, name, timeout, caller):
        # rv = 0
        # key = self.environment.fragment_cache_prefix + name

        # try to load the block from the cache
        # if there is no fragment in the cache, render it and store
        # it in the cache.
        # rv = self.environment.fragment_cache.get(key)
        # if rv is not None:
        #     return rv
        rv = caller()
        outfile = name
        print("Actually snipping to ", self.ofile, "name", name, "timeout", timeout)
        with open(name, 'w') as f:
            f.write(rv)
        # print("Actually snipping to ", self.ofile, 'writing', rv)

        # self.environment.fragment_cache.add(key, rv, timeout)
        return rv


    def _cache_support(self, name, timeout, caller):
        """Helper callback."""
        key = self.environment.fragment_cache_prefix + name

        # try to load the block from the cache
        # if there is no fragment in the cache, render it and store
        # it in the cache.
        rv = self.environment.fragment_cache.get(key)
        if rv is not None:
            return rv
        rv = caller()
        self.environment.fragment_cache.add(key, rv, timeout)
        return rv
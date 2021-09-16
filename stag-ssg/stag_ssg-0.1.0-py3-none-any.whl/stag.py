import os
import sys
import argparse
import shutil
import fnmatch
import logging
import pkgutil
from copy import deepcopy
from itertools import chain
from datetime import datetime

import tomli
from slugify import slugify

from stag.config import Config, TaxonomyTable
from stag.ecs import Page, Site, Path, Taxonomy, Metadata, Content
from stag.plugins.base import readers, generators, writers
from stag.utils import chdir, SortDate
from stag._version import version

log = logging.getLogger(__name__)


def apply_plugins(plugins, site):
    for page in site.pages:
        for plug in plugins:
            if plug.condition(page):
                log.debug(f"Running {plug.name} on page {page.url}")
                plug.plugin(page, site)


def load_plugins(path):
    for finder, name, ispkg in pkgutil.iter_modules([path]):
        mod = finder.find_module(name)
        if mod:
            mod.load_module()


def copy_output_type(pages, default="html"):
    for page in pages:
        if page.output and page.output.type:
            return page.output.type
    return default


def update_metadata(page, **kw):
    if not page.metadata:
        page.metadata = Metadata()
    kw.update(page.metadata.data)
    page.metadata.data = kw


def make_taxonomies(site):
    if not site.config.taxonomies:
        return

    taxonomies = {
        ttab.key: Taxonomy(key=ttab.key, singular=ttab.singular, plural=ttab.plural)
        for ttab in site.config.taxonomies
    }

    # We split the algorithm of creating taxonomies to 2 parts:
    #   1. gathering all the taxonomies, together with creating appropriate
    #      components
    #   2. creating page, which can be optionally already created (see below)
    #
    # This could be technically done in only one pass, but would require
    # Page.list to become a dictionary to nod add a complexity of searching
    # of term urls through the list/set of Pages

    for page in site.pages:
        if not page.metadata:
            continue
        for taxonomy in taxonomies:
            terms = page.metadata.get(taxonomy)
            if not terms:
                continue
            if not isinstance(terms, list):
                terms = [terms]
            for term in terms:
                taxonomies[taxonomy][term].add(page)

    # Pages can be created by users for taxonomies and terms. In this situation
    # stag will override some members (page.list), update others with unset
    # values (metadata) and leave the rest untouched (e.g. content).
    #
    # This is to give users possibility to hardcode custom metadata for specific
    # taxonomies.
    now = datetime.now()
    for base, taxonomy in taxonomies.items():
        baseslug = slugify(base)
        taxo_page = site.get_or_create_page(baseslug)
        taxo_page.list = []
        taxo_page.taxonomy = taxonomy
        update_metadata(taxo_page, title=taxonomy.plural, date=now)

        for term, pages in taxonomy.terms.items():
            termslug = slugify(term)
            term_page = site.get_or_create_page(f"{baseslug}/{termslug}")
            term_page.list = sorted(pages, key=SortDate)
            term_page.output = Content(type=copy_output_type(pages))
            update_metadata(term_page, title=term, date=now, taxonomy=base)

            taxo_page.list.append(term_page)

        taxo_page.list.sort()
        taxo_page.output = Content(type=copy_output_type(taxo_page.list))

    site.taxonomies = list(taxonomies.values())


def build(args, config):
    log.info(f"Building site to {config.output}")
    site = Site(config=config)

    rds = readers(config.readers)
    roots = [
        config.content,
        os.path.join(config.plugins.theme.name, "static"),
        "static",
    ]

    for root in roots:
        gather_files(root, rds, site)

    shutil.rmtree(config.output, ignore_errors=True)
    os.makedirs(config.output)

    apply_plugins(generators(config.generators), site)

    make_taxonomies(site)

    apply_plugins(writers(config.writers), site)


def serve(args, config):
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    build(args, config)
    with chdir(config.output):
        log.info(f"Running simple HTTP server on http://localhost:{args.port}.")
        server_address = ("", args.port)
        httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
        httpd.serve_forever()


def deduce_url(path):
    if path.filebase == "index":
        return path.reldirname
    else:
        slug, _ = os.path.splitext(path.basename)
        return os.path.join(path.reldirname, pat.filebase)


def gather_files(srcdir, plugins, site):
    def read_file(path):
        for plug in plugins:
            if plug.condition(path):
                log.debug(f"Reading {path.path} with {plug.name} plugin.")
                return plug.plugin(path, site)
        return None

    for curdir, _, files in os.walk(srcdir):
        for f in files:
            path = Path(os.path.join(curdir, f), srcdir)
            page = read_file(path)
            if page:
                site.add_page(page)
            else:
                log.warning(f"No valid reader for {path.path}")


def read_config(path):
    try:
        with open(path) as f:
            config = tomli.loads(f.read())
    except FileNotFoundError:
        config = {}

    return config


def make_root_config(cfg_dct):
    recognised = {}
    supported = Config.__attrs_attrs__  # bare tuple with properties for names

    user_dct = cfg_dct.pop("user", {})
    taxo_lst = cfg_dct.pop("taxonomies", [])

    for key, val in cfg_dct.items():
        if not hasattr(supported, key):
            log.error(
                f"Unrecognised option: {key}. User-defined options should be put in the [user] table."
            )
            continue
        recognised[key] = val

    cfg = Config(**recognised)
    cfg.user.__dict__.update(user_dct)
    cfg.taxonomies.extend(TaxonomyTable(**t) for t in taxo_lst)
    return cfg


def update_config_plugins(cfg, plugins_dct):
    for plugin in chain(readers(), generators(), writers()):
        if plugin.config:
            pconf = deepcopy(plugin.config)
            for key, val in plugins_dct.get(plugin.name, {}).items():
                if not hasattr(pconf, key):
                    log.error(f"Unrecognised option {key} for {plugin.name} plugin")
                    continue

                if isinstance(val, dict):
                    getattr(pconf, key).update(val)
                else:
                    setattr(pconf, key, val)
            setattr(cfg.plugins, plugin.name, pconf)

    return cfg


def prepare_args():
    parser = argparse.ArgumentParser(description="Simply Stupid Static Site Generator")
    parser.set_defaults(verbosity=logging.INFO)

    parser.add_argument(
        "-c",
        "--config",
        nargs="?",
        default="config.toml",
        help="path to stag's configuration file",
    )

    parser.add_argument(
        "-D",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="verbosity",
        help="show debug messages",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {version}")

    sp = parser.add_subparsers(required=True, dest="subcommands")

    sp_build = sp.add_parser("build")
    sp_build.set_defaults(func=build)

    sp_serve = sp.add_parser("serve")
    sp_serve.add_argument("-p", "--port", type=int, default="8000", help="HTTP port")
    sp_serve.set_defaults(func=serve)

    return parser.parse_args()


def main():
    args = prepare_args()
    logging.basicConfig(format="%(message)s", level=args.verbosity)

    cfg_dct = read_config(args.config)
    plugins_dct = cfg_dct.pop("plugins", None)

    cfg = make_root_config(cfg_dct)
    load_plugins(cfg.pluginspath)
    update_config_plugins(cfg, plugins_dct)

    try:
        return args.func(args, cfg)
    except Exception as e:
        log.error(f"Critical error: {e}")
        if args.verbosity == logging.DEBUG:
            import pdb, traceback

            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
            raise
        return 1

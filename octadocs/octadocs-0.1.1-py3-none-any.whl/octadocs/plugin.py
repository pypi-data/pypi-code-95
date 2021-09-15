import logging
import operator
from functools import lru_cache, partial
from pathlib import Path
from typing import Optional, Any, Dict, Callable

import rdflib
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from octadocs.conversions import iri_by_page, src_path_to_iri
from octadocs.default_context import construct_root_context
from octadocs.iolanta import render
from octadocs.macros import link
from octadocs.navigation.processor import OctadocsNavigationProcessor
from octadocs.octiron import Octiron
from octadocs.query import query
from octadocs.storage import DiskCacheStorage
from octadocs.stored_query import StoredQuery
from octadocs.types import LOCAL, Query, OCTA, DEFAULT_NAMESPACES
from typing_extensions import TypedDict
from rich.traceback import install

install(show_locals=False)

logger = logging.getLogger(__name__)


class ConfigExtra(TypedDict):
    """Extra portion of the config which we put our graph into."""

    graph: rdflib.ConjunctiveGraph
    octiron: Octiron
    queries: StoredQuery
    named_contexts: Dict[str, Any]


class Config(TypedDict):
    """MkDocs configuration."""

    docs_dir: str
    extra: ConfigExtra
    nav: dict   # type: ignore


class TemplateContext(TypedDict):
    """Context for the native MkDocs page rendering engine."""

    graph: rdflib.ConjunctiveGraph
    iri: rdflib.URIRef
    this: rdflib.URIRef
    query: Query
    queries: StoredQuery
    local: rdflib.Namespace
    render: Callable[[rdflib.URIRef], str]

    # FIXME this is hardcode and should be removed
    rdfs: rdflib.Namespace


def get_template_by_page(
    page: Page,
    graph: rdflib.ConjunctiveGraph,
) -> Optional[str]:
    """Find the template to render the given Markdown file."""
    iri = rdflib.URIRef(f'{LOCAL}{page.file.src_path}')

    bindings = graph.query(
        'SELECT ?template_name WHERE { ?iri octa:template ?template_name }',
        initBindings={
            'iri': iri,
        },
    ).bindings

    if bindings:
        return bindings[0]['template_name'].value

    return None


@lru_cache(None)
def cached_octiron(docs_dir: Path) -> Octiron:
    """Retrieve cached Octiron instance or create it if absent."""
    return Octiron(
        root_directory=docs_dir,
        root_context=construct_root_context(
            namespaces=DEFAULT_NAMESPACES,
        ),
    )


class OctaDocsPlugin(BasePlugin):
    """MkDocs Meta plugin."""

    octiron: Octiron
    stored_query: StoredQuery

    def on_config(self, config: Config) -> Config:
        """Initialize Octiron and provide graph to macros through the config."""
        docs_dir = Path(config['docs_dir'])

        self.octiron = cached_octiron(
            docs_dir=docs_dir,
        )

        self.stored_query = StoredQuery(
            path=docs_dir.parent / 'queries',
            executor=partial(
                query,
                instance=self.octiron.graph,
            ),
        )

        if config['extra'] is None:
            config['extra'] = {}  # type: ignore

        config['extra'].update({
            'graph': self.octiron.graph,
            'octiron': self.octiron,
            'queries': self.stored_query,
            'named_contexts': {},
        })

        return config

    def on_files(self, files: Files, config: Config):
        """Extract metadata from files and compose the site graph."""
        # Load the Octadocs vocabulary into graph
        self.octiron.update_from_file(
            path=Path(__file__).parent / 'yaml/octadocs.yaml',
            local_iri=rdflib.URIRef(OCTA),
            global_url='/octadocs.yaml',
            named_contexts=config['extra']['named_contexts'],
        )

        # And the global iolanta vocabulary
        self.octiron.update_from_file(
            path=Path(__file__).parent / 'yaml/iolanta.yaml',
            local_iri=rdflib.URIRef('https://iolanta.tech/'),
            global_url='/iolanta.yaml',
            named_contexts=config['extra']['named_contexts'],
        )

        for mkdocs_file in files:
            self.octiron.update_from_file(
                path=Path(mkdocs_file.abs_src_path),
                local_iri=src_path_to_iri(mkdocs_file.src_path),
                global_url=f'/{mkdocs_file.url}',
                named_contexts=config['extra']['named_contexts'],
            )

        self.octiron.apply_inference()

        DiskCacheStorage(octiron=self.octiron).save()

    def on_page_markdown(
        self,
        markdown: str,
        page: Page,
        config: Config,
        files: Files,
    ):
        """Inject page template path, if necessary."""
        page.iri = iri_by_page(page)

        template_name = get_template_by_page(
            page=page,
            graph=self.octiron.graph,
        )

        if template_name is not None:
            page.meta['template'] = template_name

        return markdown

    def on_page_context(
        self,
        context: TemplateContext,
        page: Page,
        config: Config,
        nav: Page,
    ) -> TemplateContext:
        """Attach the views to certain pages."""
        page_iri = rdflib.URIRef(
            f'{LOCAL}{page.file.src_path}',
        )

        this_choices = list(map(
            operator.itemgetter(rdflib.Variable('this')),
            self.octiron.graph.query(
                'SELECT * WHERE { ?this octa:subjectOf ?page_iri }',
                initBindings={
                    'page_iri': page_iri,
                },
            ).bindings,
        ))

        if this_choices:
            context['this'] = this_choices[0]
        else:
            context['this'] = page_iri

        context['graph'] = self.octiron.graph
        context['iri'] = page_iri

        # noinspection PyTypedDict
        context['query'] = partial(
            query,
            instance=self.octiron.graph,
        )
        context['queries'] = self.stored_query

        context['local'] = LOCAL
        context['LOCAL'] = LOCAL
        context.update(self.octiron.namespaces)

        context['render'] = partial(
            render,
            octiron=self.octiron,
        )

        # Provide all the support namespaces into template context
        context['octiron'] = self.octiron
        context['link'] = partial(
            link,
            octiron=self.octiron,
        )

        # Page attributes
        page.iri = page_iri

        return context

    def on_nav(
        self,
        nav: Navigation,
        config: Config,
        files: Files,
    ) -> Navigation:
        """Update the site's navigation from the knowledge graph."""
        if not config.get('nav'):
            nav = OctadocsNavigationProcessor(
                graph=self.octiron.graph,
                navigation=nav,
            ).generate()

        return nav

    def on_serve(
        self,
        server: LiveReloadServer,
        config: Config,
        builder,
    ) -> LiveReloadServer:
        inference_directory = Path(config['docs_dir']).parent / 'inference'
        if inference_directory.is_dir():
            for sparql_file in inference_directory.glob('**/*.sparql'):
                server.watch(str(sparql_file), builder)

        queries_directory = Path(config['docs_dir']).parent / 'queries'
        if queries_directory.is_dir():
            for sparql_file in queries_directory.glob('**/*.sparql'):
                server.watch(str(sparql_file), builder)

        return server

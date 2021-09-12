#!python3

import logging
import yaml
import click
from typing import List

from pathlib import Path

from elasticsearch import Elasticsearch
from rich.console import Console
from rich.text import Text
from rich.table import Table, Column
from rich import box
from rich.progress import track

from page_query.rule.manual_http_urls import ManualHttpUrls
from page_query.rule.manual_file_urls import ManualFileUrls
from page_query.rule.manual_http_urls_glob_md import ManualHttpUrlsGlobMarkdown


def update_pages(elasticsearch_stub: Elasticsearch, rules: List):
    if not elasticsearch_stub.indices.exists(index='tldr'):
        elasticsearch_stub.indices.create(index='tldr')
    
    filter = set()
    for rule in track(rules, description='checking changed rules...'):
        for page_id in rule.page_ids():
            if elasticsearch_stub.exists(index='tldr', id=page_id):
                filter.add(page_id)

    logging.info(f'keep {filter}')
    for rule in track(rules, description='request urls and update changes...'):
        for page_id, page in rule.pages(filter=filter):
            r = elasticsearch_stub.index('tldr', body=page, id=page_id)
            logging.info(f'index page {page["title"]}: {r}')
            filter.add(page_id)

    r = elasticsearch_stub.search(index='tldr',
                                  body={'query': {'match_all': {}}},
                                  _source=['_id'])
    for page in track(r['hits']['hits'], description='removeing deleted pages...'):
        if page['_id'] not in filter:
            elasticsearch_stub.delete(index='tldr', id=page['_id'])


def query_pages(elasticsearch_stub: Elasticsearch, query_string: str):
    if len(query_string) == 0:
        r = elasticsearch_stub.search(
            index='tldr',
            body={'query': {'match_all': {}}},
        )
    else:
        r = elasticsearch_stub.search(
            index='tldr',
            body={
                'query': {
                    'multi_match': {
                        'query': query_string,
                        'fields': ['title^3', 'tags^3', 'summary', 'body']
                    }
                }
            },
        )
    return r['hits']

def load_rules_from_config(config_path: str):
    path = Path(config_path)
    if not path.is_file():
        raise IOError(f'{path} is not file')
    config_text = path.read_text()
    config_dict = yaml.safe_load(config_text)

    elasticsearch_url = config_dict.get('elasticsearch_url', 'http://127.0.0.1:9200')
    elasticsearch_stub = Elasticsearch(hosts=[elasticsearch_url])

    rules = []
    for rule_dict in config_dict['rules']:
        if rule_dict['type'] == 'manual_http_urls':
            rules.append(ManualHttpUrls(title = rule_dict['title'],
                                        tags = rule_dict['tags'],
                                        summary = rule_dict['summary'],
                                        http_urls = rule_dict['http_urls']))
        elif rule_dict['type'] == 'manual_file_urls':
            rules.append(ManualFileUrls(title = rule_dict['title'],
                                        tags = rule_dict['tags'],
                                        summary = rule_dict['summary'],
                                        file_urls = rule_dict['file_urls']))
        elif rule_dict['type'] == 'manual_http_urls_glob_md':
            rules.append(ManualHttpUrlsGlobMarkdown(
                patterns=[f'{path.parent}/{p}' for p in rule_dict['glob']],
                tags=rule_dict.get('tags', [])))
        else:
            raise ValueError(f'{rule_dict["type"]} not known')
    return elasticsearch_stub, rules


def print_query_results(res: List):
    table = Table(
        Column("Id"),
        Column("Info", overflow='fold'),
        box = box.SIMPLE,
        leading = 1,
    )
    for idx, hit in enumerate(res['hits']):
        source = hit['_source']
        info = Text()
        info.append('Title: ', style='bold')
        info.append(f'{source["title"]}\n', style='sandy_brown')
        info.append('Tags: ', style='bold')
        info.append(f'{",".join(source["tags"])}\n', style='yellow4')
        info.append(f'Urls:\n', style='bold')
        for url in source.get("urls", []):
            info.append(f'- {url}\n')
        info.append('\n')
        info.append('Summary: \n\n', style='bold')
        info.append(source['summary'], style='sky_blue1')
        table.add_row(str(idx), info)
    console = Console(width=150)
    console.print(table)


@click.command()
@click.option('--config', default='page_query_config.yaml', help='the path of config file')
@click.option('--update', is_flag=True, default=False)
@click.option('--query', default='', type=str, help='query string')
def main(config: str, update: bool, query: str):
    elasticsearch_stub, rules = load_rules_from_config(config)
    if update:
        update_pages(elasticsearch_stub, rules)
    else:
        print_query_results(query_pages(elasticsearch_stub, query))

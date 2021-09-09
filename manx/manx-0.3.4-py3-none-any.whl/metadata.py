import logging
from typing import List

from elasticsearch import AsyncElasticsearch

from manx.files import MigrationFile

log = logging.getLogger("manx.metadata")
meta_index = "manx-metadata"


async def prepare(es: AsyncElasticsearch):
    """Prepare the metadata index."""
    options = {
        "settings": {"index": {"hidden": "true"}},
        "mappings": {
            "properties": {
                "stamp": {"type": "integer"},
                "name": {"type": "keyword"},
                "sha3": {"type": "keyword"},
                "alias": {"type": "keyword"},
                "applied_at": {"type": "date"},
                "config": {"type": "flattened"},
            }
        },
    }

    # Ignore the "already exists" error
    return await es.indices.create(meta_index, options, ignore=400)


async def get(alias: str, es: AsyncElasticsearch) -> List[MigrationFile]:
    """Return the metadata for a given alias"""
    res = await es.search(
        {"query": {"match": {"alias": alias}}},
        index=meta_index,
        size=1000,
        sort="stamp:asc",
    )

    migrations = []
    for record in res["hits"]["hits"]:
        source = record["_source"]
        stamp = source["stamp"]
        name = source["name"]
        sha3 = source["sha3"]
        config = source["config"]
        mf = MigrationFile(stamp, name, None, sha3, config=config)
        migrations.append(mf)

    migrations.sort(key=lambda m: m.stamp)
    return migrations


async def delete(alias: str, es: AsyncElasticsearch):
    """Delete the metadata for a given alias"""
    query = {"query": {"match": {"alias": alias}}}
    return await es.delete_by_query(body=query, index=meta_index)

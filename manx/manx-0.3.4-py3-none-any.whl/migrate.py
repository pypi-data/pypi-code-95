import logging
from typing import Dict, Generator, Iterator

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk, async_scan

from manx import metadata
from manx.configs import get_all_configs
from manx.exceptions import ManxException
from manx.files import MigrationFile, get_python_files

log = logging.getLogger("manx.migrate")
meta_index = "manx-metadata"


async def create_new_index(
    alias: str, migration_package: str, es: AsyncElasticsearch, custom_config: Dict = {}
):
    py_migrations = get_python_files(migration_package)
    configs = await get_all_configs(migration_package)
    final_stamp, final_config = next(reversed(configs.items()))
    if custom_config:
        final_config = custom_config

    # Create new index
    new_index_name = f"{alias}-{final_stamp}"
    await es.indices.create(index=new_index_name, body=final_config)
    await es.indices.put_alias(index=new_index_name, name=alias)

    # Log manx metadata
    for migration in py_migrations:
        if migration.stamp == final_stamp:
            config = final_config
        else:
            config = configs[migration.stamp]
        meta = migration.to_meta_doc(alias, config)
        await es.index(meta_index, meta)


async def migrate_index(alias: str, migration_package: str, es: AsyncElasticsearch):
    py_migrations = get_python_files(migration_package)
    previous = await metadata.get(alias, es)
    gen = next_migration_generator(py_migrations, iter(previous))

    if previous:
        last_applied = previous[-1]
    else:
        last_applied = None

    configs = await get_all_configs(migration_package, last_applied)

    for migration in gen:
        config = configs[migration.stamp]
        await _apply(alias, migration, config, es)


def next_migration_generator(
    migrations: Iterator[MigrationFile], previously_applied: Iterator[MigrationFile]
) -> Generator[MigrationFile, None, None]:
    mig = next(migrations, False)
    prev = next(previously_applied, False)

    # Iterate until both sequences are fully consumed
    while mig or prev:
        if not mig:
            log.warn(
                f"MISSING Previously applied migration {prev.stamp}-{prev.name} no longer exists"
            )
            prev = next(previously_applied, False)
            continue

        if not prev:
            log.info(f"EXECUTE {mig.stamp}-{mig.name}")
            yield mig
            mig = next(migrations, False)
            continue

        stampdiff = mig.stamp - prev.stamp
        if stampdiff == 0:
            if mig.hash_ == prev.hash_:
                log.info(
                    f"MATCH   Skipping previously applied migration {mig.stamp}-{mig.name}"
                )
            else:
                log.warn(
                    f"BADHASH Previously applied migration {mig.stamp}-{mig.name} with hash {prev.hash_} but now hash is {mig.hash_}"
                )
            mig = next(migrations, False)
            prev = next(previously_applied, False)
        elif stampdiff > 0:
            log.warn(
                f"MISSING Previously applied migration {prev.stamp}-{prev.name} no longer exists"
            )
            prev = next(previously_applied, False)
        elif stampdiff < 0:
            log.warn(
                f"RETCON  Skipping {mig.stamp}-{mig.name} because a newer migration ({prev.stamp}-{prev.name}) was previously applied"
            )
            mig = next(migrations, False)


async def _apply(
    alias: str,
    migration_file: MigrationFile,
    config: Dict,
    es: AsyncElasticsearch,
):
    # Find old index name
    get_alias = await es.indices.get_alias(alias)
    old_index_name = list(get_alias)[0]

    # Create new index
    new_index_name = f"{alias}-{migration_file.stamp}"
    await es.indices.create(index=new_index_name, body=config)

    try:
        # Prevent insertion of new documents in the old index
        await es.indices.add_block(old_index_name, "write")

        # Use the bulk helper and the generator
        await async_bulk(
            es, _new_doc_generator(alias, new_index_name, migration_file, es)
        )

        if "verify" in migration_file.module.__dir__():
            success = await migration_file.module.verify(es)
            if not success:
                msg = f"Verification failed in {migration_file}"
                raise ManxException(msg)
    except Exception as e:
        log.error(str(e))
        log.error(f"  Removing write block from {old_index_name}")
        await es.indices.put_settings(
            index=old_index_name, body={"blocks": {"write": None}}
        )
        log.error(f"  Deleting {new_index_name}")
        await es.indices.delete(new_index_name)
        raise e

    # Everything worked, now move the alias to the new index
    # Order the next operations to minimize downtime
    if old_index_name == alias:
        # The bootstrap case, where an index exists without an alias
        await es.indices.delete(old_index_name)
        await es.indices.put_alias(index=new_index_name, name=alias)
    else:
        # The normal case, where manx is managing the aliases
        await es.indices.delete_alias(index=old_index_name, name=alias)
        await es.indices.put_alias(index=new_index_name, name=alias)
        await es.indices.delete(old_index_name)

    # Log the successful migration in manx metadata index
    await es.index(meta_index, migration_file.to_meta_doc(alias, config))


async def _new_doc_generator(
    alias: str,
    new_index_name: str,
    migration_file: MigrationFile,
    es: AsyncElasticsearch,
):
    # Scan over every document in the old index, update it, and insert it into the new index
    scan = async_scan(es, query={"query": {"match_all": {}}}, index=alias)
    async for old_doc in scan:
        new_doc = await migration_file.module.up_doc(es, old_doc["_source"])
        if isinstance(new_doc, list):
            # up_doc returned a list of docs
            for d in new_doc:
                d["_index"] = new_index_name
                yield d
        else:
            # up_doc returned a single doc
            new_doc["_index"] = new_index_name
            yield new_doc

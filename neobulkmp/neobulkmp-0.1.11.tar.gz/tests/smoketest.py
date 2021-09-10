import sys
import os

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
from neobulkmp import Manager, WorkerSourcing
import sys
import os
import logging
import graphio
import py2neo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-15s %(processName)-8s %(module)-8s %(levelname)-8s:  %(message)s",
    handlers=[logging.StreamHandler((sys.stdout))],
)

dbhost = os.getenv("CI_DB_HOST", "localhost")
g = py2neo.Graph(**{"host": dbhost})


def assert_result():
    r = g.run("MATCH (n:Actor) RETURN count(n) as cnt").data()[0]["cnt"]
    assert r == 12
    r = g.run("MATCH (n:Movie) RETURN count(n) as cnt").data()[0]["cnt"]
    assert r == 5
    r = g.run("MATCH (a:Actor)-[ai:ACTS_IN]->(m:Movie) RETURN count(ai) as cnt").data()[
        0
    ]["cnt"]
    assert r == 15


def clean_db():
    g.run("DROP INDEX Movie IF EXISTS")
    g.run("DROP INDEX Actor IF EXISTS")
    g.run("MATCH p=()-[:ACTS_IN]->() DELETE p")
    g.run("MATCH (a:Actor) DELETE a")
    g.run("MATCH (a:Movie) DELETE a")


def run_smoketest():

    movies = []
    movies.append(
        {
            "title": "Matrix",
            "Actors": ["Keanu Reeves", "Carrie-Anne Moss", "Laurence Fishburne"],
        }
    )
    movies.append(
        {
            "title": "Bill & Ted's Excellent Adventure",
            "Actors": ["Keanu Reeves", "Alex Winter", "George Carlin"],
        }
    )

    movies.append(
        {
            "title": "Ghost in the Shell",
            "Actors": ["Atsuko Tanaka", "Akio Otsuka", "Iemasa Kayumi"],
        }
    )

    movies.append(
        {"title": "Dogma", "Actors": ["Ben Affleck", "Jason Lee", "George Carlin"]}
    )
    movies.append(
        {
            "title": "Almost Famous",
            "Actors": ["Patrick Fugit", "Jason Lee", "Frances McDormand"],
        }
    )

    def parsing_func(worker: WorkerSourcing, title, Actors):
        # Create nodeset with movie
        log = worker.get_logger()
        movieset = graphio.NodeSet(["Movie"], merge_keys=["title"])
        movieset.add_node({"title": title})
        # Send Nodeset with movie to neobulkmp manager
        yield movieset
        # Create Actor Nodeset and connect actors to movie
        actorset = graphio.NodeSet(["Actor"], merge_keys=["name"])
        acts_in_movie = graphio.RelationshipSet(
            "ACTS_IN", ["Actor"], ["Movie"], ["name"], ["title"]
        )
        for actor in Actors:
            actorset.add_node({"name": actor})
            acts_in_movie.add_relationship({"name": actor}, {"title": title}, {})

        # Send actorset to neobulkmp manager
        yield actorset
        # Send actor to movie relation to neobulkmp manager
        yield acts_in_movie

    # Mount parsing function on parsing workers
    WorkerSourcing.sourcing_func = parsing_func

    # Init manager, provide parsing worker and worker parameters
    cachehost = os.getenv("CI_CACHE_HOST", "localhost")
    print("CACHE:HOST:", cachehost)
    manager = Manager(
        worker_sourcing_class=WorkerSourcing,
        worker_parameters=movies,
        cache_backend_params={"host": cachehost},
    )
    manager.status_log_every_n_sec = 1
    # manager.max_concurrently_worker_count = 1
    manager.create_indexes = True
    dbhost = os.getenv("CI_DB_HOST", "localhost")
    # manager.create_unique_constraints = True  # not yet implemented
    manager.merge(graph_params={"host": dbhost})


# clean_db()
run_smoketest()
assert_result()

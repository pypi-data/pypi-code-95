# Demo Script for neobulkmp
# This Script will insert some movies with a sample of actors with multiple processes
# Requirements:
# * neobulkmp installed `pip install neobulkmp`
# * A local neo4j DB as database `docker run --rm --network host -e NEO4J_AUTH=none neo4j`
# * A local redis DB as a loading cache `docker run --rm --network=host redis`

from neobulkmp import Manager, WorkerSourcing
import sys
import os
import logging
import graphio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-15s %(processName)-8s %(module)-8s %(levelname)-8s:  %(message)s",
    handlers=[logging.StreamHandler((sys.stdout))],
)


movies = []
movies.append(
    {
        "title": "Matrix",
        "Actors": ["Keanu Reeves", "Carrie-Anne Moss", "Laurence Fishburne"],
    }
)
movies.append(
    {
        "title": "Ghost in the Shell",
        "Actors": ["Atsuko Tanaka", "Akio Otsuka", "Iemasa Kayumi"],
    }
)
movies.append(
    {
        "title": "Bill & Ted's Excellent Adventure",
        "Actors": ["Keanu Reeves", "Alex Winter", "George Carlin"],
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


class MyCustomWorker(WorkerSourcing):
    def sourcing_func(worker, title, Actors):
        # Create nodeset with movie
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


# Init manager, provide parsing worker and worker parameters
manager = Manager(worker_sourcing_class=MyCustomWorker, worker_parameters=movies)
# manager.max_concurrently_worker_count = 1
manager.create_indexes = True
# manager.create_unique_constraints = True  # not yet implemented
manager.merge(graph_params={"host": "localhost"})

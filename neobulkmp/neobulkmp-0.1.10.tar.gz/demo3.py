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
import dict2graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-15s %(processName)-8s %(module)-8s %(levelname)-8s:  %(message)s",
    handlers=[logging.StreamHandler((sys.stdout))],
)


data = {
    "MedlineCitation": {
        "Status": "PubMed-not-MEDLINE",
        "Owner": "NLM",
        "PMID": {"Version": "1", "text": "20764441"},
        "DateCompleted": {"Year": "2011", "Month": "03", "Day": "29"},
        "DateRevised": {"Year": "2011", "Month": "03", "Day": "29"},
        "Article": {
            "PubModel": "Print",
            "Journal": {
                "ISSN": {"IssnType": "Print", "text": "0007-1447"},
                "JournalIssue": {
                    "CitedMedium": "Print",
                    "Volume": "1",
                    "Issue": "2522",
                    "PubDate": {"Year": "1909", "Month": "May", "Day": "01"},
                },
                "Title": "British medical journal",
                "ISOAbbreviation": "Br Med J",
            },
            "ArticleTitle": "BILATERAL NEPHRO-LITHOTOMY, IN WHICH THE KIDNEY WAS KEPT OUTSIDE THE WOUND FOR SEVEN DAYS BEFORE RETURNING IT TO THE LOIN.",
            "Pagination": {"MedlinePgn": "1059-60"},
            "AuthorList": {
                "CompleteYN": "Y",
                "Author": [
                    {
                        "ValidYN": "Y",
                        "LastName": "Clay",
                        "ForeName": "J",
                        "Initials": "J",
                    }
                ],
            },
            "Language": ["eng"],
            "PublicationTypeList": {
                "PublicationType": [{"UI": "D016428", "text": "Journal Article"}]
            },
        },
        "MeshHeadingList": {
            "MeshHeading": [
                {
                    "DescriptorName": {
                        "UI": "D000311",
                        "MajorTopicYN": "N",
                        "text": "Adrenal Glands",
                    },
                    "QualifierName": [
                        {"UI": "Q000601", "MajorTopicYN": "Y", "text": "surgery"}
                    ],
                },
                {
                    "DescriptorName": {
                        "UI": "D013507",
                        "MajorTopicYN": "Y",
                        "text": "Endocrine Surgical Procedures",
                    }
                },
                {
                    "DescriptorName": {
                        "UI": "D006801",
                        "MajorTopicYN": "N",
                        "text": "Humans",
                    }
                },
                {
                    "DescriptorName": {
                        "UI": "D008216",
                        "MajorTopicYN": "Y",
                        "text": "Lymphocytic Choriomeningitis",
                    }
                },
                {
                    "DescriptorName": {
                        "UI": "D008581",
                        "MajorTopicYN": "Y",
                        "text": "Meningitis",
                    }
                },
            ]
        },
        "MedlineJournalInfo": {
            "Country": "England",
            "MedlineTA": "Br Med J",
            "NlmUniqueID": "0372673",
            "ISSNLinking": "0007-1447",
        },
    },
    "PubmedData": {
        "History": {
            "PubMedPubDate": [
                {
                    "PubStatus": "entrez",
                    "Year": "2010",
                    "Month": "8",
                    "Day": "27",
                    "Hour": "6",
                    "Minute": "0",
                },
                {
                    "PubStatus": "pubmed",
                    "Year": "1909",
                    "Month": "5",
                    "Day": "1",
                    "Hour": "0",
                    "Minute": "0",
                },
                {
                    "PubStatus": "medline",
                    "Year": "1909",
                    "Month": "5",
                    "Day": "1",
                    "Hour": "0",
                    "Minute": "1",
                },
            ]
        },
        "PublicationStatus": "ppublish",
        "ArticleIdList": {
            "ArticleId": [
                {"IdType": "pubmed", "text": "20764441"},
                {"IdType": "pmc", "text": "PMC2318724"},
            ]
        },
    },
}
"""
data = {
    "MedlineCitation": {
        "Status": "PubMed-not-MEDLINE",
        "Owner": "NLM",
        "PMID": {"Version": "1", "text": "20764441"},
        "DateCompleted": {"Year": "2011", "Month": "03", "Day": "29"},
        "DateRevised": {"Year": "2011", "Month": "03", "Day": "29"},
        "Article": {
            "PubModel": "Print",
            "Journal": {
                "ISSN": {"IssnType": "Print", "text": "0007-1447"},
                "JournalIssue": {
                    "CitedMedium": "Print",
                    "Volume": "1",
                    "Issue": "2522",
                    "PubDate": {"Year": "1909", "Month": "May", "Day": "01"},
                },
                "Title": "British medical journal",
                "ISOAbbreviation": "Br Med J",
            },
        },
        "AuthorList": {
            "CompleteYN": "Y",
            "Author": [
                {
                    "ValidYN": "Y",
                    "LastName": "Clay",
                    "ForeName": "J",
                    "Initials": "J",
                }
            ],
        },
    }
}
"""


class MyCustomWorker(WorkerSourcing):
    def sourcing_func(worker, srcdata):
        d2g = dict2graph.Dict2graph()
        d2g.parse(srcdata, "Movie", instant_save=False)
        d2g.save()
        for nodeSet in d2g.nodeSets.values():
            yield nodeSet
            # worker.cache.store_NodeSet(nodeSet)

        for relSet in d2g.relationshipSets.values():
            yield relSet
            # worker.cache.store_RelSet(relSet)
        d2g.clear()


# Init manager, provide parsing worker and worker parameters
manager = Manager(
    worker_sourcing_class=MyCustomWorker, worker_parameters=[{"srcdata": data}]
)
# manager.max_concurrently_worker_count = 1
manager.create_indexes = True
# manager.create_unique_constraints = True  # not yet implemented
manager.merge(graph_params={"host": "localhost"})

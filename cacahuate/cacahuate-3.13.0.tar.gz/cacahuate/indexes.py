import pymongo


def create_indexes(config):
    # Create index
    uri = config['MONGO_URI']

    with pymongo.MongoClient(uri) as client:
        database_name = pymongo.uri_parser.parse_uri(uri)['database']
        db = client[database_name]

        db.execution.create_index("id", unique=True)
        db.execution.create_index("status")
        db.execution.create_index("started_at")
        db.execution.create_index("finished_at")

        db.pointer.create_index("status")
        db.pointer.create_index("execution.id")
        db.pointer.create_index("started_at")
        db.pointer.create_index("finished_at")

import os
from DZDutils.neo4j import wait_for_db_boot
db_host = os.getenv("CI_DB_HOST", "localhost")
wait_for_db_boot({"host": db_host}, timeout_sec=120)

import sqlq


sqlqueue = sqlq.SqlQueueU(server=True, db="db.db", depth=2)
input("stop? ")
sqlqueue.commit()
sqlqueue.stop()

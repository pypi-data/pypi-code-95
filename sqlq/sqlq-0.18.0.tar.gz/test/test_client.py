import sqlq


sqlqueue = sqlq.SqlQueueU()
sqlqueue.sql("CREATE TABLE IF NOT EXISTS `test` (`col` TEXT);")
sqlqueue.sql("DELETE FROM `test`;")
sqlqueue.sql("INSERT INTO `test` VALUES (?);", ("test1 23",))
r = sqlqueue.sql("SELECT * FROM `test`;")
print(r)
r = sqlqueue.sql("SELECT * FROM `test` WHERE `col` LIKE ?;", ("%23",), "list")
print(r)
sqlqueue.commit()
sqlqueue.stop()

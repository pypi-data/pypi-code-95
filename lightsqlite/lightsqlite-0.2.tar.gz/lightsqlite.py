import sqlite3


def try_type(s):
    # 若传入value（j）的类型为str，则在字符串内容两侧加入表示内容的引号
    if type(s) != str:
        return s
    else:
        return "'%s'" % s.replace("'", "\\'")


def format_condition_into_sql(s: dict, sp="and", prefix="WHERE"):
    """
    格式化SQL子句
    name: SQL子句的前缀（也就是转换后的任意前缀）
    sp: SQL条件之间的分隔符，可取"and"或"or"
    """
    if not s:
        # 传入字典为空，则无需设置查询条件
        return ""
    result = ""
    for i, j in s.items():
        t = try_type(j)
        if type(t) in [str, int, float]:
            # 这些类型无需处理即可直接传入
            result += "`%s`=%s %s " % (i, t, sp)
        elif type(t) == list:
            # 若字典当前项value为列表，则数据库的table中当前列（i）可对应当前value（j）列表中的任意一项
            text = "("
            for k in t:
                text += "`%s`=%s or " % (i, try_type(k))
            result += "%s) %s " % (text[:-len(" or ")], sp)
        else:
            raise TypeError
    return prefix + " " + result[:-(len(sp) + 2)]


class Connect:
    database = "test.db"

    def __init__(self, database="test.db", check_same_thread=False):
        # 连接和游标的初始化
        self.database = database
        self.check_same_thread = check_same_thread
        self.connect = sqlite3.connect(
            self.database, check_same_thread=self.check_same_thread)
        print("连接到 %s 成功！" % self.database)

    def run_code(self, code, return_result=True):
        cursor = self.connect.cursor()
        cursor.execute(code)
        self.connect.commit()
        if not return_result:
            return None
        results = []
        result = cursor.fetchone()
        while result:
            results.append(result)
            result = cursor.fetchone()
        return results

    def insert(self, table: str, data: dict):
        # 分别将字典的key和value格式化为SQL语句
        keys = ", ".join("`%s`" % t for t in data.keys())
        values = ", ".join(
            ("'%s'" % (t.replace("'", "\\'") if type(t) == str else t))
            for t in data.values())
        return self.run_code("INSERT INTO '%s' (%s) VALUES (%s);" %
                             (table, keys, values))

    def select(self,
               table,
               target: list or str = [],
               condition: dict = {},
               condition_sp="and",
               limit=""):
        # 若只传入table，则语句等价于SELECT * FROM table;
        if type(target) == str:
            target = [target]
        condition = format_condition_into_sql(condition, condition_sp)
        if limit:
            limit = "limit " + limit
        return self.run_code("SELECT %s FROM '%s' %s %s;" %
                             ((target and "`" + "`,`".join(target) + "`")
                              or "*", table, condition, limit))

    def update(self,
               table,
               changes: dict = {},
               condition: dict = {},
               condition_sp="and"):
        changes = format_condition_into_sql(changes, sp=",", prefix="")
        condition = format_condition_into_sql(condition, condition_sp)
        return self.run_code("UPDATE %s SET %s %s;" %
                             (table, changes, condition))

    def delete(self, table, condition: dict, condition_sp="and"):
        condition = format_condition_into_sql(condition, condition_sp)
        return self.run_code("DELETE FROM %s %s;" % (table, condition))

    def restart(self):
        self.connect = sqlite3.connect(self.database)
        print("连接到 %s 成功！" % self.database)

    def close(self):
        del (self)

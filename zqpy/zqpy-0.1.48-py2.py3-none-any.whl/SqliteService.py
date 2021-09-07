import sqlite3

class SqliteServiceClass(object):
    def __init__(self):
        self.conn = None
        self.cursor = None

    def OpenSql(self, dbName):
        '''打开/创建 数据库'''
        try:
            # global conn, cursor
            self.conn = sqlite3.connect(dbName)
            self.cursor = self.conn.cursor()
            return True
        except BaseException as e:
            print(str(e))
            return False

    def CloseSql(self):
        '''关闭数据库'''
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            return True
        except BaseException as e:
            print(str(e))
            return False

    def CreateTable(self, tabName, fields, attribute, size, defaultValue, isUniqueId):
        '''创建表'''
        try:
            if not self.cursor:
                return False
            strValue = ''
            for index in range(0, len(fields)):
                strValue = strValue + '%s %s %s %s %s '%(fields[index], attribute[index], '' if not size or len(size) < len(fields) else '(%s)'%size[index], '' if index!=0 else 'primary key %s'%('UNIQUE' if isUniqueId else ''), ',' if index!=len(fields)-1 else '') #defaultValue[index]
            self.cursor.execute('create table %s (%s)'%(tabName, strValue))
            return True
        except BaseException as e:
            print(str(e))
            return False

    def DestoryTable(self, tabName):
        '''删除表'''
        try:
            if not self.cursor:
                return False
            self.cursor.execute('drop table %s'%(tabName))
            self.conn.commit()
            return True
        except BaseException as e:
            print(str(e))
            return False

    def InsertData(self, tabName, values):
        '''
        插入数据
        values -> [(),()]
        '''
        try:
            if not self.cursor:
                return False
            strValue = ''
            for index in range(0, len(values[0])):
                strValue = strValue + ('?' if index==0 else ',?')
            self.cursor.executemany('INSERT INTO %s VALUES (%s)'%(tabName, strValue), values)
            self.conn.commit()
            return True
        except BaseException as e:
            print(str(e))
            return False

    def DelData(self, tabName, key, value):
        '''删除数据'''
        try:
            if not self.cursor:
                return False
            self.cursor.execute('DELETE FROM %s WHERE %s=%s'%(tabName, key, value))
            self.conn.commit()
            return True
        except BaseException as e:
            print(str(e))
            return False

    #字符串最好用双引号
    def UpdateData(self, tabName, key, value, fields, values):
        '''更新数据'''
        try:
            if not self.cursor:
                return False
            strValue = ''
            for index in range(0, len(fields)):
                strValue = strValue + ('%s=%s,' if index!=len(fields)-1 else '%s=%s')%(fields[index], values[index] if type(values[index])!='str' else '\"%s\"'%values[index])   
            self.cursor.execute('UPDATE %s SET %s WHERE %s=%s'%(tabName, strValue, key, value))
            self.conn.commit()
            return True
        except BaseException as e:
            print(str(e))
            return False

    def SelectData(self, tabName, fields, keys, values, marks = False):       
        '''
        查询数据
        marks [1,-1] 1 and  -1 or
        '''
        try:
            if not self.cursor:
                return False
            strValue = ''
            for index in range(0, len(fields)):
                strValue = strValue + ('%s,' if index!=len(fields)-1 else '%s')%(fields[index])
            whereValue = ''
            if keys and values:
                for index in range(0, len(keys)):
                    whereValue = whereValue + ('WHERE ' if index==0 else '') + ('%s=%s '%(str(keys[index]),str(values[index]))) + ('' if not marks or index>=len(marks) else ('and ' if marks[index]==1 else 'or ' ))
            self.cursor.execute(('SELECT %s FROM %s '%('*' if len(fields)==0 else strValue, tabName)) + whereValue)
            return self.cursor.fetchall()
        except BaseException as e:
            print(str(e))
            return []
            
    def SelectSingData(self, tabName, fields, keys, values, marks = False):       
        '''
        查询满足的单行数据
        marks [1,-1] 1 and  -1 or
        '''
        data = self.SelectData(tabName, fields, keys, values, marks)
        return None if len(data) == 0 else data[0]

    def GetTableRecordNum(self, tabName):
        '''获取表中记录数'''
        try:
            if not self.cursor:
                return False
            self.cursor.execute('SELECT count(*) FROM %s'%(tabName))
            return self.cursor.fetchone()[0]
        except BaseException as e:
            print(str(e))
            return 0

    def IsExistsTable(self, tabName):
        '''是否存在表'''
        try:
            if not self.cursor:
                return False
            self.cursor.execute('SELECT count(*) FROM %s'%(tabName))
            return len(self.cursor.fetchall()) != 0
        except BaseException as e:
            print(str(e))
            return False

    def IsExistsData(self, tabName, keys, values):
        '''数据是否存在于表中'''
        try:
            if not self.cursor:
                return False
            selectData = self.SelectData(tabName, [], keys, values)
            return selectData and len(selectData) != 0
        except BaseException as e:
            print(str(e))
            return False

if __name__ == "__main__":
    sql = SqliteServiceClass()
    print('%s -> %s'%('OpenSql', sql.OpenSql('Test.db')))
    print('%s -> %s'%('CreateTable', sql.CreateTable('TestTable', ['id', 'name'], ['int', 'text'], [10, 20], [], True)))
    print('%s -> %s'%('InsertData', sql.InsertData('TestTable', [(1,'5555'),(2,'666'),(3,'777'),(5,'5555999')])))
    print('%s -> %s'%('GetTableRecordNum', sql.GetTableRecordNum('TestTable')))
    print('%s -> %s'%('IsExistsTable', sql.IsExistsTable('TestTable')))
    print('%s -> %s'%('IsExistsTable', sql.IsExistsTable('TestTable1')))
    print('%s -> %s'%('IsExistsData', sql.IsExistsData('TestTable', ['id'], [1])))
    print('%s -> %s'%('UpdateData',sql.UpdateData('TestTable', 'id', 1, ['id', 'name'],[11,'11'])))
    print('%s -> %s'%('DelData', sql.DelData('TestTable', 'id', 11)))
    print('%s -> %s'%('SelectData', sql.SelectData('TestTable', ['id','name'], ['id'], [5])))
    print('%s -> %s'%('SelectData', sql.SelectData('TestTable', [], False, False)))
    print('%s -> %s'%('DestoryTable', sql.DestoryTable('TestTable')))
    print('%s -> %s'%('CloseSql', sql.CloseSql()))
    import os
    os.remove('Test.db')
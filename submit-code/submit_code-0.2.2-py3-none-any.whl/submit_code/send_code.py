import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from IPython import get_ipython
from datetime import datetime
import time
import os

license_path = os.path.dirname(__file__)
cred = credentials.Certificate('{}/web-project-c3c1a-firebase-adminsdk-9j2mf-e202997418.json'.format(license_path))
firebase_admin.initialize_app(cred, {'databaseURL': 'https://web-project-c3c1a-default-rtdb.asia-southeast1.firebasedatabase.app'})

ip = get_ipython() 

class DbManager:

    def __init__(self, user_id = "", title = "", code = "", nowDateTime = ""):
        self.user_id = user_id
        self.title = title
        self.code = code
        self.nowDateTime = nowDateTime

    def Update(self):
        data_dic = {
                self.title : {
                    "user_id" : self.user_id,
                    "id" : int(time.time()),
                    "date" :  self.nowDateTime,
                    "text" : self.code,
                }
            }
        user_ref = db.reference('code')
        user_ref.update(data_dic)

    def GetData(self):
        code_ref = db.reference('code')
        snapshot = code_ref.order_by_child('id').get()
        for key, val in snapshot.items():
            print("{} : {}".format(key, val))

def ExtractCode() : # Jupyter 코드 작성 Cell 코드 추출
        codes = []
        run_history = ip.history_manager.get_range()
        for code in run_history :
            codes.append(code[2])
        return codes[-1]

def PrintCode(code, nowDateTime) :
    print("#-----------Code-----------")
    print(code)
    print("#--------------------------")
    print(nowDateTime, "제출완료" )

def Submit(user_id, title) :
    now = datetime.now()
    nowDateTime = now.strftime('%Y-%m-%d %H:%M:%S\n')
    code = ExtractCode()
    Db = DbManager(user_id, title, code, nowDateTime)
    Db.Update()
    PrintCode(code, nowDateTime)
    raise SystemExit("제출 완료에 따른 정상적인 Cell 실행 중지")


import requests
class nlp:
    def __init__(self,token):
        '''token: str (get your API token from http://openapi.botnoi.ai/)
        '''
        self.token = token
    def chitchat(self,message,styleid,botname):
        ''' input message: str
                 styleid: int
                 botname: str
            styleid meaning
                {0: 'กระเทย',
                 1: 'กวนทีน',
                 2: 'คุณตา',
                 3: 'คุณยาย',
                 4: 'จอมยุทธชาย',
                 5: 'ทอม',
                 6: 'ทางการ (ชาย)',
                 7: 'ทางการ (หญิง)',
                 8: 'นายก',
                 9: 'ฝรั่ง',
                 10: 'วัยรุ่น',
                 11: 'สาวขี้อ้อน',
                 12: 'สาวพูดเพราะ',
                 13: 'สาวสก็อย',
                 14: 'สาวห้าว',
                 15: 'สาวอ่อนหวาน',
                 16: 'สาวเซ็กซี่',
                 17: 'สาวใส ๆ',
                 18: 'สุภาพ (ชาย)',
                 19: 'สุภาพ (หญิง)',
                 20: 'หนุ่มขี้เล่น',
                 21: 'หนุ่มพูดเพราะ',
                 22: 'หนุ่มแว้น',
                 23: 'หยาบ',
                 24: 'หยาบมาก',
                 25: 'หลวงพ่อ',
                 26: 'หล่อ ๆ',
                 27: 'ห้วน',
                 28: 'เข้ม ๆ',
                 29: 'เจ้าหญิง',
                 30: 'เด็กชาย',
                 31: 'เด็กหญิง',
                 32: 'เพื่อนกูรักมึง'}
        '''
        url = "https://openapi.botnoi.ai/service-api/botnoichitchat?keyword=%s&styleid=%s&botname=%s"%(message,styleid,botname)
        headers = {
            'Authorization': 'Bearer %s'%self.token
        }
        response = requests.request("GET", url, headers=headers).json()
        return response
    def intentecommerce(self,message):
        url = "https://openapi.botnoi.ai/botnoi/ecommerce?keyword=%s"%message
        headers = {
            'Authorization': 'Bearer %s'%self.token
        }
        response = requests.request("GET", url, headers=headers).json()
        return response

    def sentiment(self,message):
        url = "https://openapi.botnoi.ai/botnoi/sentiment?keyword=%s"%message
        headers = {
            'Authorization': 'Bearer %s'%self.token
        }
        response = requests.request("GET", url, headers=headers).json()
        return response

    def namegender(self,name):
        url = "https://openapi.botnoi.ai/service-api/bn_nameapi?name=%s"%name
        headers = {
            'Authorization': 'Bearer %s'%self.token
        }
        response = requests.request("GET", url, headers=headers).json()
        return response







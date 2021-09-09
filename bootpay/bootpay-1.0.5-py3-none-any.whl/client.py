import requests
import uuid 
import json
from bootpay import bankcode
import time 

class Bootpay:
    base_url = {
        'development': 'https://dev-api.bootpay.co.kr',
        'production': 'https://api.bootpay.co.kr'
    }

    def __init__(self, application_id, private_key, mode='production'):
        self.application_id = application_id
        self.pk = private_key
        self.mode = mode
        self.token = None

    def api_url(self, uri=None):
        if uri is None:
            uri = []
        return '/'.join([self.base_url[self.mode]] + uri)

    # 1. 토큰 발급 
    def get_access_token(self):
        data = {
            'application_id': self.application_id,
            'private_key': self.pk
        }
        response = requests.post(self.api_url(['request', 'token']), data=data)
        result = response.json()
        if result['status'] == 200:
            self.token = result['data']['token']
        return result

    # 2. 결제 검증 
    def verify(self, receipt_id):
        return requests.get(self.api_url(['receipt', receipt_id]), headers={
            'Authorization': self.token
        }).json()

    # 3. 결제 취소 (전액 취소 / 부분 취소)
    #
    # price - (선택사항) 부분취소 요청시 금액을 지정, 미지정시 전액 취소 (부분취소가 가능한 PG사, 결제수단에 한해 적용됨)
    # cancel_id - (선택사항) 부분취소 요청시 중복 요청을 방지하기 위한 고유값
    # refund - (선택사항) 가상계좌 환불요청시, 전제조건으로 PG사와 CMS 특약이 체결되어 있을 경우에만 환불요청 가능, 기본적으로 가상계좌는 결제취소가 안됨 
    #        {
    #            account: '6756010101234', # 환불받을 계좌번호 
    #            accountholder: '홍길동', # 환불받을 계좌주
    #            bankcode: bankcode.dictionary['국민은행'], # 은행 코드 
    #        }
    #
    def cancel(self, receipt_id, price=None, name=None, reason=None, cancel_id=str(uuid.uuid4()), tax_free=None, refund=None):
        payload = {'receipt_id': receipt_id, # 부트페이로부터 받은 영수증 ID
                   'price': price, # 부분취소시 금액 지정 
                   'name': name, # 취소 요청자 이름
                   'reason': reason, # 취소 요청 사유
                   'tax_free': tax_free, # 취소할 비과세 금액 
                   'cancel_id': cancel_id, # 부분취소 중복요청 방지 
                   'tax_free': tax_free, # 취소할 비과세 금액
                   'refund': refund} 

        return requests.post(self.api_url(['cancel.json']), data=payload, headers={
            'Authorization': self.token
        }).json()


    # 4. 빌링키 발급 
    # extra - 빌링키 발급 옵션 
    #      {
    #               subscribe_tst_payment: 0, # 100원 결제 후 결제가 되면 billing key를 발행, 결제가 실패하면 에러
    #               raw_data: 0 //PG 오류 코드 및 메세지까지 리턴
    #      }  
    def get_subscribe_billing_key(self, pg, order_id, item_name, card_no, card_pw, expire_year, expire_month,identify_number, 
                                  user_info=None, extra=None):
        if user_info is None:
            user_info = {}
        payload = {
            'order_id': order_id, # 개발사에서 관리하는 고유 주문 번호
            'pg': pg, # PG사의 Alias ex) danal, kcp, inicis 등
            'item_name': item_name, # 상품명
            'card_no': card_no, # 카드 일련번호
            'card_pw': card_pw, # 카드 비밀번호 앞 2자리
            'expire_year': expire_year, # 카드 유효기간 년
            'expire_month': expire_month, # 카드 유효기간 월
            'identify_number': identify_number, # 주민등록번호 또는 사업자번호
            'user_info': user_info, # 구매자 정보 
            'extra': extra # 기타 옵션 
        }
        return requests.post(self.api_url(['request', 'card_rebill.json']), data=json.dumps(payload), headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()
    

    
    # 4-1. 발급된 빌링키로 결제 승인 요청 
    # tax_free - 면세 상품일 경우 해당만큼의 금액을 설정 
    # interest - 웰컴페이먼츠 전용, 무이자여부를 보내는 파라미터가 있다
    # quota - 5만원 이상 결제건에 적용하는 할부개월수. 0-일시불, 1은 지정시 에러 발생함, 2-2개월, 3-3개월... 12까지 지정가능
    # feedback_url - webhook 통지시 받으실 url 주소 (localhost 사용 불가)
    # feedback_content_type - webhook 통지시 받으실 데이터 타입 (json 또는 urlencoded, 기본값 urlencoded)
    #####
    def subscribe_billing(self, billing_key, item_name, price, order_id, items=None, user_info=None, extra=None,
                          tax_free=None, quota=None, interest=None, feedback_url=None, feedback_content_type=None):
        if items is None:
            items = {}
        payload = {
            'billing_key': billing_key, # 발급받은 빌링키
            'item_name': item_name, # 결제할 상품명
            'price': price, #  결제할 상품금액
            'order_id': order_id, # 개발사에서 지정하는 고유주문번호
            'items': items, # 구매할 상품정보, 통계용
            'user_info': user_info, # 구매자 정보, 특정 PG사의 경우 구매자 휴대폰 번호를 필수로 받는다
            'extra': extra, # 기타 옵션 
            'tax_free': tax_free, # 면세 상품일 경우 해당만큼의 금액을 설정
            'quota': quota, # int 형태, 5만원 이상 결제건에 적용하는 할부개월수. 0-일시불, 1은 지정시 에러 발생함, 2-2개월, 3-3개월... 12까지 지정가능
            'interest': interest, # 웰컴페이먼츠 전용, 무이자여부를 보내는 파라미터가 있다
            'feedback_url': feedback_url, # webhook 통지시 받으실 url 주소 (localhost 사용 불가)








            'feedback_content_type': feedback_content_type # webhook 통지시 받으실 데이터 타입 (json 또는 urlencoded, 기본값 urlencoded)
        }
        return requests.post(self.api_url(['subscribe', 'billing.json']), data=json.dumps(payload), headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()

    # 4-2. 발급된 빌링키로 결제 예약 요청
    # def subscribe_billing_reserve(self, billing_key, item_name, price, order_id, execute_at, feedback_url, items=None):
    def subscribe_billing_reserve(self, billing_key, item_name, price, order_id, execute_at=time.time() + 10, items=None, user_info=None, extra=None,
                        tax_free=None, quota=None, interest=None, feedback_url=None, feedback_content_type=None):
        if items is None:
            items = []
        payload = {
            'billing_key': billing_key, # 발급받은 빌링키
            'item_name': item_name, # 결제할 상품명
            'price': price, #  결제할 상품금액
            'order_id': order_id, # 개발사에서 지정하는 고유주문번호
            'execute_at': execute_at # 결제 수행(예약) 시간, 기본값으로 10초 뒤 결제 
            'items': items, # 구매할 상품정보, 통계용
            'user_info': user_info, # 구매자 정보, 특정 PG사의 경우 구매자 휴대폰 번호를 필수로 받는다
            'extra': extra, # 기타 옵션 
            'tax_free': tax_free, # 면세 상품일 경우 해당만큼의 금액을 설정
            'quota': quota, # int 형태, 5만원 이상 결제건에 적용하는 할부개월수. 0-일시불, 1은 지정시 에러 발생함, 2-2개월, 3-3개월... 12까지 지정가능
            'interest': interest, # 웰컴페이먼츠 전용, 무이자여부를 보내는 파라미터가 있다
            'feedback_url': feedback_url, # webhook 통지시 받으실 url 주소 (localhost 사용 불가)
            'feedback_content_type': feedback_content_type, # webhook 통지시 받으실 데이터 타입 (json 또는 urlencoded, 기본값 urlencoded)
            'scheduler_type': 'oneshot'            
        }
        return requests.post(self.api_url(['subscribe', 'billing', 'reserve.json']), data=json.dumps(payload), headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()

    # 4-2-1. 발급된 빌링키로 결제 예약 - 취소 요청 
    def subscribe_billing_reserve_cancel(self, reserve_id):
        return requests.delete(self.api_url(['subscribe', 'billing', 'reserve', reserve_id]), headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()


    # 4-3. 빌링키 삭제 
    def destroy_subscribe_billing_key(self, billing_key):
        return requests.delete(self.api_url(['subscribe', 'billing', billing_key]), headers={
            'Authorization': self.token
        }).json()


    # 5. (부트페이 단독 - 간편결제창, 생체인증 기반의 사용자를 위한) 사용자 토큰 발급 
    def get_user_token(self, data={}):
        return requests.post(self.api_url(['request', 'user', 'token.json']), data=data, headers={
            'Authorization': self.token
        }).json()

    # 6. 결제링크 생성 
    def request_payment(self, payload={}):
        return requests.post(self.api_url(['request', 'payment.json']), data=payload, headers={
            'Authorization': self.token
        }).json()


    # 7. 서버 승인 요청 
    def submit(self, receipt_id):
        payload = {
            'receipt_id': receipt_id
        }
        return requests.post(self.api_url(['submit.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    
    # 8. 본인 인증 결과 검증 
    def certificate(self, receipt_id):
        return requests.get(self.api_url(['certificate', receipt_id]), headers={
            'Authorization': self.token
        }).json()

    
    # deprecated 
    def remote_link(self, payload={}, sms_payload=None):
        if sms_payload is None:
            sms_payload = {}
        payload['sms_payload'] = sms_payload
        return requests.post(self.api_url(['app', 'rest', 'remote_link.json']), data=payload).json()

    # deprecated 
    def remote_form(self, remoter_form, sms_payload=None):
        if sms_payload is None:
            sms_payload = {}
        payload = {
            'application_id': self.application_id,
            'remote_form': remoter_form,
            'sms_payload': sms_payload
        }
        return requests.post(self.api_url(['app', 'rest', 'remote_form.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    # deprecated 
    def send_sms(self, receive_numbers, message, send_number=None, extra={}):
        payload = {
            'data': {
                'sp': send_number,
                'rps': receive_numbers,
                'msg': message,
                'm_id': extra['m_id'],
                'o_id': extra['o_id']
            }
        }
        return requests.post(self.api_url(['push', 'sms.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    # deprecated 
    def send_lms(self, receive_numbers, message, subject, send_number=None, extra={}):
        payload = {
            'data': {
                'sp': send_number,
                'rps': receive_numbers,
                'msg': message,
                'sj': subject,
                'm_id': extra['m_id'],
                'o_id': extra['o_id']
            }
        }
        return requests.post(self.api_url(['push', 'lms.json']), data=payload, headers={
            'Authorization': self.token
        }).json()


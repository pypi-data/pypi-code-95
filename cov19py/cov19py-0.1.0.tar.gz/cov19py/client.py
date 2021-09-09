import json
import aiohttp
import datetime
import xmltodict


def now():
    return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')


class Client:
    def __init__(self, token: str):
        self.token = token
        self.BASE_URL: str = f'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson?serviceKey={token}'

    async def todayCorona(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.BASE_URL}&startCreateDt={now()}&endCreateDt={now()}') as res:
                response = await res.text()
                return json.loads(json.dumps(xmltodict.parse(response)))

import requests
from functional import seq
from functional.streams import Sequence
from lxml import etree


def safe_xpath(n, xpath, default=None):
    try:
        return trim_whitespace(n.xpath(xpath)[0].text)
    except (RuntimeError, IndexError):
        return default


def no_whitespace():
    return str.maketrans({chr(13): '', chr(10): '', chr(9): ''})


def trim_whitespace(s: str):
    if s is None:
        return None
    else:
        return s.translate(str.maketrans({chr(13): '', chr(10): '', chr(9): ''}))


def get_comment(tr) -> str:
    textarea = tr.xpath("td[6]/textarea")
    if len(textarea) == 0:
        return trim_whitespace(tr.xpath("td[6]")[0].text)
    else:
        return trim_whitespace(textarea[0].text)


def get_duration(tr) -> float:
    select = tr.xpath("td[8]/select")

    if len(select) == 0:
        hours = safe_xpath(tr, "td[8]").split(":")[0]
        minutes = safe_xpath(tr, "td[8]").split(":")[1]
    else:
        hours = safe_xpath(select[0], "option[@selected]", "0.0")
        minutes = safe_xpath(select[1], "option[@selected]", "0.0")

    return (float(hours) * 60 + float(minutes)) / 60.0


def get_order_by_number(orders: Sequence, number: str):
    order = orders.filter(lambda o: o["number"] == number).head_option()
    if order is None:
        return {
            "number": number
        }
    else:
        return order


class Connection(object):
    def __init__(self, user, password, url):
        self.auth = (
            user,
            password
        )

        self.logged_in = False
        self.contract = None
        self.employee = None
        self.orders = None
        self.sub_orders = None
        self.contract_orders = None
        self.url = f"{url}/%s"

        self.session = requests.Session()

    def __enter__(self):
        if not self.logged_in:
            payload = {
                "loginname": self.auth[0],
                "password": self.auth[1]
            }
            self.session.post(url=self.url % "LoginEmployee", data=payload, auth=self.auth)
            self.logged_in = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.logged_in:
            self.session.post(url=self.url % "LogoutEmployee", auth=self.auth)
            self.logged_in = False

    def get_employee(self):
        if self.employee is not None:
            return self.employee

        response = self.session.post(url=self.url % 'ShowEmployee', auth=self.auth,
                                     params={"task": "refresh"},
                                     data={"filter": self.auth[0]})
        if not response.ok:
            raise RuntimeError(f"get employee id failed with status code {response.status_code}")
        else:
            root = etree.fromstring(response.content, etree.HTMLParser())
            employees = seq(root.xpath(f"//div[@class='tooltip']/../..")) \
                .map(lambda n: {
                    "id": n.xpath("td//tr/td[text()='id:']/following-sibling::td")[0].text,
                    "firstname": n.xpath("td[2]")[0].text.translate(no_whitespace()),
                    "lastname": n.xpath("td[3]")[0].text.translate(no_whitespace())
                })
            if employees.len() != 1:
                raise RuntimeError(f"one employee expected, found {employees.len()}")
            else:
                self.employee = employees.first()
                return self.employee

    def get_contract(self):
        if self.contract is not None:
            return self.contract

        response = self.session.post(url=self.url % 'ShowEmployeecontract', auth=self.auth,
                                     params={"task": "refresh"},
                                     data={"employeeId": self.get_employee()["id"]})
        if not response.ok:
            raise RuntimeError(f"get contract id failed with status code {response.status_code}")
        else:
            root = etree.fromstring(response.content, etree.HTMLParser())
            contracts = seq(root.xpath(f"//div[@class='tooltip']/../..")) \
                .map(lambda n: {
                    "id": n.xpath("td//tr/td[text()='id:']/following-sibling::td")[0].text,
                    "job": n.xpath("td[3]")[0].text.translate(no_whitespace()),
                    "hours": float(n.xpath("td[8]")[0].text)
                })
            if contracts.len() != 1:
                raise RuntimeError(f"one contract expected, found {contracts.len()}")
            else:
                self.contract = contracts.first()
                return self.contract

    def get_contract_orders(self) -> Sequence:
        if self.contract_orders is not None:
            return self.contract_orders

        response = self.session.post(url=self.url % "ShowEmployeeorder", auth=self.auth,
                                     params={"task": "refresh"},
                                     data={"employeeContractId": self.get_contract()["id"]})
        if not response.ok:
            raise RuntimeError(f"get contract sub orders failed with status code {response.status_code}")
        else:
            root = etree.fromstring(response.content, etree.HTMLParser())
            self.contract_orders = seq(root.xpath("//table//td/div[@class='tooltip']/../..")) \
                .map(lambda n: {
                    "id": n.xpath("td//tr/td[text()='id:']/following-sibling::td")[0].text,
                    "order": {
                        "number": n.xpath("td[3]")[0].text,
                        "short": n.xpath("td[5]")[0].text
                    },
                    "sub_order": {
                        "number": n.xpath("td[4]")[0].text,
                        "short": n.xpath("td[6]")[0].text
                    }
                })
            return self.contract_orders

    def get_orders(self) -> Sequence:
        if self.orders is not None:
            return self.orders

        response = self.session.get(url=self.url % 'ShowCustomerorder', auth=self.auth)
        if not response.ok:
            raise RuntimeError(f"get sub orders failed with status code {response.status_code}")
        else:
            root = etree.fromstring(response.content, etree.HTMLParser())
            self.orders = seq(root.xpath("//table//td/div[@class='tooltip']/../..")) \
                .map(lambda n: {
                    "id": n.xpath("td//tr/td[text()='id:']/following-sibling::td")[0].text,
                    "customer": n.xpath("td//tr/td[text()='Auftraggeber:']/following-sibling::td")[0].text,
                    "number": n.xpath("td//tr/td[text()='Auftrag:']/following-sibling::td")[0].text,
                })
            return self.orders

    def get_sub_orders(self) -> Sequence:
        if self.sub_orders is not None:
            return self.sub_orders

        response = self.session.get(url=self.url % 'ShowSuborder', auth=self.auth)
        if not response.ok:
            raise RuntimeError(f"get sub orders failed with status code {response.status_code}")
        else:
            root = etree.fromstring(response.content, etree.HTMLParser())
            self.sub_orders = seq(root.xpath("//table//td/div[@class='tooltip']/../..")) \
                .map(lambda n: {
                    "id": n.xpath("td//tr/td[text()='id:']/following-sibling::td")[0].text,
                    "order": get_order_by_number(self.get_orders(),
                                                 n.xpath("td//tr/td[text()='Auftrag:']/following-sibling::td")[0].text),
                    "number": n.xpath("td[3]")[0].text,
                    "short": n.xpath("td[5]")[0].text
                })
            return self.sub_orders

    def create_report(self, suborder, comment, day, duration_hours=1, duration_minutes=0):
        response = self.session.get(url=self.url % "CreateDailyReport", auth=self.auth)

        if not response.ok:
            raise RuntimeError(f"create report failed with status code {response.status_code}")

        payload = {
            "employeeContractId": self.get_contract()["id"],
            "referenceday": day,
            "numberOfSerialDays": "0",
            "orderId": suborder["order"]["id"],
            "suborderSignId": suborder["id"],
            "selectedHourDuration": duration_hours,
            "selectedMinuteDuration": duration_minutes,
            "costs": "0.0",
            "comment": comment,
            "id": "0",
        }
        parameter = {
            "task": "save",
            "continue": "false"
        }

        response = self.session.post(url=self.url % "StoreDailyReport", auth=self.auth, params=parameter, data=payload)
        if not response.ok:
            raise RuntimeError(f"store report failed with status code {response.status_code}")

    def get_report(self, contract, start_day, end_day):
        response = self.session.get(url=self.url % "ShowDailyReport", auth=self.auth)
        if not response.ok:
            raise RuntimeError(f"show report failed with status code {response.status_code}")

        payload = {
            "employeeContractId": contract["id"],
            "startdate": start_day,
            "enddate": end_day,
            "order": "ALL+ORDERS",
            "orderId": "0",
            "view": ["custom", "custom"],
            "showOnlyValid": "on"
        }
        parameter = {
            "task": "refreshTimereports"
        }
        response = self.session.post(url=self.url % "ShowDailyReport", auth=self.auth, params=parameter, data=payload)
        if not response.ok:
            raise RuntimeError(f"show report failed with status code {response.status_code}")
        else:
            root = etree.fromstring(response.content, etree.HTMLParser())
            return seq(root.xpath("//table//td/div[@class='tooltip']/../..")) \
                .map(lambda n: {
                    "id": n.xpath("td//tr/td[text()='id:']/following-sibling::td")[0].text.translate(no_whitespace()),
                    "date": str(n.xpath("td[2]/following::text()[4]")[0]).translate(no_whitespace()),
                    "order": {
                        "number": str(n.xpath("td[3]/following::text()[3]")[0]).translate(no_whitespace()),
                        "order_short": str(n.xpath("td[4]/following::text()[3]")[0]).translate(no_whitespace())
                    },
                    "sub_order": {
                        "number": str(n.xpath("td[3]/following::text()[4]")[0]).translate(no_whitespace()),
                        "short": str(n.xpath("td[4]/following::text()[4]")[0]).translate(no_whitespace()),
                    },
                    "comment": get_comment(n),
                    "duration": get_duration(n)
                })

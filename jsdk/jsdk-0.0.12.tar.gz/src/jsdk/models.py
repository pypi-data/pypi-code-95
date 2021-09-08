from typing import ForwardRef, List, Optional, Union

JasminUser = ForwardRef('JasminUser')
JasminFilter = ForwardRef('JasminFilter')
JasminGroup = ForwardRef('JasminGroup')
JasminMTRoute = ForwardRef('JasminMTRoute')


class JasminGroup(object):
    gid: str
    is_active: bool

    @classmethod
    def from_line(cls, line: List[str]) -> JasminGroup:
        group = cls()
        group.gid = line[0].replace('#', '').replace('!', '')
        group.is_active = not line[0].startswith('#!')

        return group


class JasminUser(object):
    gid: str
    throughput_summary: str
    username: str
    uid: str
    is_active: bool

    # MT Authorization
    http_send: bool
    http_balance: bool
    http_rate: bool
    http_bulk: bool
    smpps_send: bool
    http_long_content: bool
    dlr_level: bool
    http_dlr_method: bool
    src_addr: bool
    priority: bool
    validity_period: bool
    schedule_delivery_time: bool
    hex_content: bool

    # MT Valuefilter
    valuefilter_dst_addr: str
    valuefilter_src_addr: str
    valuefilter_priority: str
    valuefilter_validity_period: str
    valuefilter_content: str

    # MT defaultvalue
    defaultvalue_src_addr: str

    # MT quota
    quota_balance: Union[float, str]
    quota_early_percent: float
    quota_sms_count: Union[int, str]
    quota_http_throughput: int
    quota_smpps_throughput: int

    # smpps_cred bind
    authorization_bind: bool
    quota_max_bindings: int

    @classmethod
    def from_line(cls, line: List[str]) -> JasminUser:
        user = cls()
        user.quota_balance = line[3] if line[3] == 'ND' else float(line[3])
        user.quota_sms_count = line[5] if line[
                                              3] == 'ND' and line[4] == '(!)' else line[4]
        user.username = line[2]
        user.throughput_summary = line[7] if line[3] == 'ND' and line[5] == 'ND' else line[5]
        user.gid = line[1].replace('!', '')
        user.uid = line[0].replace('#', '').replace('!', '')
        user.is_active = line[0].startswith('#!')

        return user

    @classmethod
    def from_inspect(cls, data: List[List[str]]):
        user = cls()
        user.mt_sms = None
        user.username = data[2][-1]
        user.quota_balance = data[-7][-1]
        user.quota_sms_count = data[-5][-1]
        user.quota_early_percent = data[-6][-1]
        user.quota_smpps_throughput = data[-3][-1]
        user.quota_http_throughput = data[-4][-1]
        user.throughput_summary = data[-4][-1] + '/' + data[-4][-1]
        user.gid = data[1][-1]
        user.uid = data[0][-1]
        user.is_active = None

        user.http_send = data[3][-1] == 'True'
        user.http_balance = data[4][-1] == 'True'
        user.http_rate = data[5][-1] == 'True'
        user.http_bulk = data[6][-1] == 'True'
        user.smpps_send = data[7][-1] == 'True'
        user.http_long_content = data[8][-1] == 'True'
        user.dlr_level = data[9][-1] == 'True'
        user.http_dlr_method = data[10][-1] == 'True'
        user.src_addr = data[11][-1] == 'True'
        user.priority = data[12][-1] == 'True'
        user.validity_period = data[13][-1] == 'True'
        user.schedule_delivery_time = data[14][-1] == 'True'
        user.hex_content = data[15][-1] == 'True'

        user.valuefilter_dst_addr = data[16][-1]
        user.valuefilter_src_addr = data[17][-1]
        user.valuefilter_priority = data[18][-1]
        user.valuefilter_validity_period = data[16][-1]
        user.valuefilter_content = data[19][-1]

        user.defaultvalue_src_addr = data[-8][-1]

        user.authorization_bind = data[-2][-1] == 'True'
        user.quota_max_bindings = data[-1][-1]

        return user


class JasminMTRoute(object):
    order: int
    type: str
    rate: Union[float, str]
    connector: str
    filter: Optional[str]

    @classmethod
    def from_line(cls, line: List[str]) -> JasminMTRoute:
        mt_route = cls()
        mt_route.order = line[0].replace('#', '')
        mt_route.rate = line[2]
        mt_route.connector = line[4] if line[3] == '(!)' else line[3]
        try:
            if line[3] == '(!)' and line[5]:
                mt_route.filter = f'{line[5]} {line[6]}'
            if line[3] != '(!)' and line[4]:
                mt_route.filter = f'{line[4]} {line[5]}'
        except IndexError:
            mt_route.filter = None
        mt_route.type = line[1]

        return mt_route


class JasminFilter(object):
    fid: str
    type: str
    routes: str
    description: str

    @classmethod
    def from_line(cls, line: List[str]) -> JasminFilter:
        jfilter = cls()
        jfilter.fid = line[0].replace('#', '')
        jfilter.type = line[1]
        jfilter.routes = f'{line[2]} {line[3]}'
        jfilter.description = f'{line[4]} {line[5]}'.replace(
            '<', '').replace('>', '')

        return jfilter


class JasminSMPPConnector(object):
    con_fail_delay: int = None
    dlr_expiry: int = None
    coding: int = None
    submit_throughput: int = None
    elink_interval: int = None
    bind_to: int = None
    port: int = None
    con_fail_retry: str = None
    password: str = None
    src_addr: str = None
    bind_npi: int = None
    addr_range: str = None
    dst_ton: int = None
    res_to: int = None
    def_msg_id: int = None
    priority: int = None
    con_loss_retry: str = None
    username: str = None
    dst_npi: int = None
    validity: int = None
    requeue_delay: int = None
    host: str = None
    src_npi: int = None
    trx_to: int = None
    logfile: str = None
    systype: str = None
    cid: str = None
    loglevel: int
    bind: str = None
    proto_id: int = None
    con_loss_delay: int = None
    bind_ton: int = None
    pdu_red_to: int = None
    src_ton: int = None
    logrotate: str = None
    logprivacy: str = None
    con_loss_delay: int = None
    ripf: int = None
    coding: str = None
    dlr_msgid: int = None
    ssl: str = None

    is_running: bool
    session: str = None
    starts: int = None
    stops: int = None

    @classmethod
    def from_line(cls, line: List[str]):
        connector = cls()
        connector.cid = line[0].replace('#', '')
        connector.is_running = line[1] == 'started'
        connector.session = line[2]
        connector.starts = line[3]
        connector.stops = line[4]

        return connector

    @classmethod
    def from_inspect(cls, line: List[List[str]]):
        connector = cls()
        connector.con_fail_delay = line[16][-1]
        connector.dlr_expiry = line[-6][-1]
        connector.coding = line[-9][-1]
        connector.submit_throughput = line[-7][-1]
        connector.elink_interval = line[11][-1]
        connector.bind_to = line[10][-1]
        connector.port = line[2][-1]
        connector.con_fail_retry = line[-4][-1]
        connector.password = line[5][-1]
        connector.src_addr = line[24][-1]
        connector.bind_npi = line[14][-1]
        connector.addr_range = line[23][-1]
        connector.dst_ton = line[22][-1]
        connector.res_to = line[12][-1]
        connector.def_msg_id = line[31][-1]
        connector.priority = line[26][-1]
        connector.con_loss_retry = line[13][-1]
        connector.username = line[3][-1]
        connector.dst_npi = line[-3][-1]
        connector.validity = line[29][-1]
        connector.requeue_delay = line[-8][-1]
        connector.host = line[1][-1]
        connector.src_npi = line[21][-1]
        connector.trx_to = line[-2][-1]
        connector.logfile = line[7][-1]
        connector.systype = line[6][-1]
        connector.cid = line[0][-1]
        connector.loglevel = line[8][-1]
        connector.bind = line[18][-1]
        connector.proto_id = line[25][-1]
        connector.con_loss_delay = line[15][-1]
        connector.bind_ton = line[19][-1]
        connector.pdu_red_to = line[17][-1]
        connector.src_ton = line[20][-1]
        connector.logrotate = line[4][-1]
        connector.logprivacy = line[9][-1]
        connector.ripf = line[30][-1]
        connector.dlr_msgid = line[-5][-1]
        connector.ssl = line[1][-1]

        return connector

from contextlib import contextmanager
import sys
from typing import List
from enum import Enum

import pexpect
from pexpect import spawn, ExceptionPexpect

from .models import *
from .exceptions import JasminException


class MTRouteType(str, Enum):
    DefaultRoute = 'DefaultRoute'
    StaticMTRoute = 'StaticMTRoute'
    RandomRoundrobinMTRoute = 'RandomRoundrobinMTRoute'
    FailoverMTRoute = 'FailoverMTRoute'


class FilterType(str, Enum):
    TransparentFilter = 'TransparentFilter'
    ConnectorFilter = 'ConnectorFilter'
    UserFilter = 'UserFilter'
    GroupFilter = 'GroupFilter'
    SourceAddrFilter = 'SourceAddrFilter'
    DestinationAddrFilter = 'DestinationAddrFilter'
    ShortMessageFilter = 'ShortMessageFilter'
    DateIntervalFilter = 'DateIntervalFilter'
    TimeIntervalFilter = 'TimeIntervalFilter'
    TagFilter = 'TagFilter'
    EvalPyFilter = 'EvalPyFilter'


class JasminManager(object):
    child: spawn = None
    __base_cmd__ = ''
    debug_mode: bool = False

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: str = 8990,
                 username='jcliadmin',
                 password='jclipwd') -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @contextmanager
    def connect(self):
        try:
            self.child = pexpect.spawn(
                'telnet {host} {port}'.format(host=self.host, port=self.port))
            self.child.sendline(self.username)
            self.child.sendline(self.password)

            if self.debug_mode:
                self.child.logfile = sys.stdout.buffer

            yield self.child
        except ExceptionPexpect as exc:
            raise JasminException('Unable to connect to jasmin service') from exc
        finally:
            if self.child:
                self.child.sendline('persist')
                self.child.sendline('quit')

    def add(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def remove(self, *args, **kwargs):
        raise NotImplementedError

    def list(self, *args, **kwargs):
        raise NotImplementedError

    def inspect(self, id: str):
        raise NotImplementedError

    def _parse_list(self, pattern: str):
        list_lines: List[List[str]] = []
        self.child.expect([pattern, pexpect.TIMEOUT])
        # Exclude header info
        raw_data = [out.decode('utf-8')
                    for out in self.child.before.split(b'\r\r\r\n')][10:]
        for line in raw_data:
            if line == '':
                continue
            list_lines.append([data for data in line.split(' ') if data != ''])

        return list_lines

    def _parse_inspect(self):
        inspect_lines: List[List[str]] = []
        self.child.expect([pexpect.TIMEOUT], timeout=1)
        # Exclude header info
        raw_data = [out.decode('utf-8')
                    for out in self.child.before.split(b'\r\r\r\n')][9:]

        if 'Unknown' in raw_data[0]:
            return False

        for line in raw_data:
            if line.startswith('jcli'):
                continue
            inspect_lines.append([data for data in line.split(' ') if data != ''])

        return inspect_lines

    def _get_operation_status(self) -> bool:
        try:
            self.child.expect(['Successfully', pexpect.TIMEOUT], timeout=1)

            if 'Successfully' not in self.child.after.decode():
                return False

            return True
        except AttributeError:
            return False

    def set_debug_mode(self, status: bool = False):
        self.debug_mode = status


class JasminUserManager(JasminManager):
    __base_cmd__ = 'user'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, username: str, password: str, gid: str,
            http_send=True, http_balance=True, http_rate=True,
            http_bulk=True, smpps_send=True, http_long_content=True,
            dlr_level=True, http_dlr_method=True, src_addr=True,
            priority=True, validity_period=True, schedule_delivery_time=True,
            hex_content=True, dst_addr='.*', valuefilter_src_addr='.*',
            valuefilter_priority='^[0-3]$', valuefilter_validity_period='^\d+$',
            content='.*', defaultvalue_src_addr: str = None, balance: int = None,
            early_percent: float = None, sms_count: int = None, http_throughput: int = None,
            smpps_throughput: int = None, bind=True, max_bindings: int = None) -> bool:
        """Create a new user

        Args:
            username (str): 
            password (str): 
            gid (str): 
            http_send (bool, optional): Defaults to True.
            http_balance (bool, optional): Defaults to True.
            http_rate (bool, optional): Defaults to True.
            http_bulk (bool, optional): Defaults to True.
            smpps_send (bool, optional): Defaults to True.
            http_long_content (bool, optional): Defaults to True.
            dlr_level (bool, optional): Defaults to True.
            http_dlr_method (bool, optional): Defaults to True.
            src_addr (bool, optional): Defaults to True.
            priority (bool, optional): Defaults to True.
            validity_period (bool, optional): Defaults to True.
            schedule_delivery_time (bool, optional): Defaults to True.
            hex_content (bool, optional): Defaults to True.
            dst_addr (str, optional): Defaults to '.*'.
            valuefilter_src_addr (str, optional): Defaults to '.*'.
            valuefilter_priority (str, optional): Defaults to '^[0-3]$'.
            valuefilter_validity_period (str, optional): Defaults to '^\d+$'.
            content (str, optional): Defaults to '.*'.
            defaultvalue_src_addr (str, optional): Defaults to None.
            balance (int, optional): Defaults to None.
            early_percent (float, optional): Defaults to None.
            sms_count (int, optional): Defaults to None.
            http_throughput (int, optional): Defaults to None.
            smpps_throughput (int, optional): Defaults to None.
            bind (bool, optional): Defaults to True.
            max_bindings (int, optional): Defaults to None.

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} --add')
            child.sendline(f'username {username}')
            child.sendline(f'uid {username}')
            child.sendline(f'password {password}')
            child.sendline(f'gid {gid}')

            child.sendline(
                f'mt_messaging_cred authorization http_send {http_send}')
            child.sendline(
                f'mt_messaging_cred authorization http_balance {http_balance}')
            child.sendline(
                f'mt_messaging_cred authorization http_rate {http_rate}')
            child.sendline(
                f'mt_messaging_cred authorization http_bulk {http_bulk}')
            child.sendline(
                f'mt_messaging_cred authorization smpps_send {smpps_send}')
            child.sendline(
                f'mt_messaging_cred authorization http_long_content {http_long_content}')
            child.sendline(
                f'mt_messaging_cred authorization dlr_level {dlr_level}')
            child.sendline(
                f'mt_messaging_cred authorization http_dlr_method {http_dlr_method}')
            child.sendline(
                f'mt_messaging_cred authorization src_addr {src_addr}')
            child.sendline(
                f'mt_messaging_cred authorization priority {priority}')
            child.sendline(
                f'mt_messaging_cred authorization validity_period {validity_period}')
            child.sendline(
                f'mt_messaging_cred authorization schedule_delivery_time {schedule_delivery_time}')
            child.sendline(
                f'mt_messaging_cred authorization hex_content {hex_content}')

            child.expect(['>'])

            child.sendline(
                f'mt_messaging_cred valuefilter dst_addr {dst_addr}')
            child.sendline(
                f'mt_messaging_cred valuefilter src_addr {valuefilter_src_addr}')
            child.sendline(
                f'mt_messaging_cred valuefilter priority {valuefilter_priority}')
            child.sendline(
                f'mt_messaging_cred valuefilter validity_period {valuefilter_validity_period}')
            child.sendline(
                f'mt_messaging_cred valuefilter content {content}')
            child.sendline(
                f'mt_messaging_cred defaultvalue src_addr {defaultvalue_src_addr}')

            child.sendline(f'mt_messaging_cred quota balance {balance}')
            child.sendline(
                f'mt_messaging_cred quota early_percent {early_percent}')
            child.sendline(
                f'mt_messaging_cred quota sms_count {sms_count}')
            child.sendline(
                f'mt_messaging_cred quota http_throughput {http_throughput}')
            child.sendline(
                f'mt_messaging_cred quota smpps_throughput {smpps_throughput}')
            child.sendline(f'smpps_cred authorization bind {bind}')
            child.sendline(
                f'smpps_cred quota max_bindings {max_bindings}')

            child.sendline('ok')

        return self._get_operation_status()

    def update(self, username: str, password: str = None, gid: str = None,
               http_send: bool = None, http_balance: bool = None, http_rate: bool = None,
               http_bulk: bool = None, smpps_send: bool = None, http_long_content: bool = None,
               dlr_level: bool = None, http_dlr_method: bool = None, src_addr: bool = None,
               priority: bool = None, validity_period: bool = None, schedule_delivery_time: bool = None,
               hex_content: bool = None, dst_addr: str = None, valuefilter_src_addr: str = None,
               valuefilter_priority: str = None, valuefilter_validity_period: str = None,
               content: str = None, defaultvalue_src_addr: str = None, balance: int = None,
               early_percent: float = None, sms_count: int = None, http_throughput: int = None,
               smpps_throughput: int = None, bind: bool = None, max_bindings: int = None) -> bool:
        """Update a user by its id

        Args:
            username (str):
            password (str, optional): Defaults to None.
            gid (str, optional): Defaults to None.
            http_send (bool, optional): Defaults to None.
            http_balance (bool, optional): Defaults to None.
            http_rate (bool, optional): Defaults to None.
            http_bulk (bool, optional): Defaults to None.
            smpps_send (bool, optional): Defaults to None.
            http_long_content (bool, optional): Defaults to None.
            dlr_level (bool, optional): Defaults to None.
            http_dlr_method (bool, optional): Defaults to None.
            src_addr (bool, optional): Defaults to None.
            priority (bool, optional): Defaults to None.
            validity_period (bool, optional): Defaults to None.
            schedule_delivery_time (bool, optional): Defaults to None.
            hex_content (bool, optional): Defaults to None.
            dst_addr (str, optional): Defaults to None.
            valuefilter_src_addr (str, optional): Defaults to None.
            valuefilter_priority (str, optional): Defaults to None.
            valuefilter_validity_period (str, optional): Defaults to None.
            content (str, optional): Defaults to None.
            defaultvalue_src_addr (str, optional): Defaults to None.
            balance (int, optional): Defaults to None.
            early_percent (float, optional): Defaults to None.
            sms_count (int, optional): Defaults to None.
            http_throughput (int, optional): Defaults to None.
            smpps_throughput (int, optional): Defaults to None.
            bind (bool, optional): Defaults to None.
            max_bindings (int, optional): Defaults to None.

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -u {username}')
            if gid:
                child.sendline(f'gid {gid}')
            if password:
                child.sendline(f'password {password}')
            if http_send is not None:
                child.sendline(
                    f'mt_messaging_cred authorization http_send {http_send}')
            if http_balance is not None:
                child.sendline(
                    f'mt_messaging_cred authorization http_balance {http_balance}')
            if http_rate is not None:
                child.sendline(
                    f'mt_messaging_cred authorization http_rate {http_rate}')
            if http_bulk is not None:
                child.sendline(
                    f'mt_messaging_cred authorization http_bulk {http_bulk}')
            child.sendline(
                f'mt_messaging_cred authorization smpps_send {smpps_send}')
            if http_long_content is not None:
                child.sendline(
                    f'mt_messaging_cred authorization http_long_content {http_long_content}')
            if dlr_level is not None:
                child.sendline(
                    f'mt_messaging_cred authorization dlr_level {dlr_level}')
            if http_dlr_method is not None:
                child.sendline(
                    f'mt_messaging_cred authorization http_dlr_method {http_dlr_method}')
            if src_addr is not None:
                child.sendline(
                    f'mt_messaging_cred authorization src_addr {src_addr}')
            if priority is not None:
                child.sendline(
                    f'mt_messaging_cred authorization priority {priority}')
            if validity_period is not None:
                child.sendline(
                    f'mt_messaging_cred authorization validity_period {validity_period}')
            if schedule_delivery_time is not None:
                child.sendline(
                    f'mt_messaging_cred authorization schedule_delivery_time {schedule_delivery_time}')
            if hex_content is not None:
                child.sendline(
                    f'mt_messaging_cred authorization hex_content {hex_content}')

            child.expect(['>'])

            if dst_addr:
                child.sendline(
                    f'mt_messaging_cred valuefilter dst_addr {dst_addr}')
            if valuefilter_src_addr:
                child.sendline(
                    f'mt_messaging_cred valuefilter src_addr {valuefilter_src_addr}')
            if valuefilter_priority:
                child.sendline(
                    f'mt_messaging_cred valuefilter priority {valuefilter_priority}')
            if valuefilter_validity_period:
                child.sendline(
                    f'mt_messaging_cred valuefilter validity_period {valuefilter_validity_period}')
            if content:
                child.sendline(
                    f'mt_messaging_cred valuefilter content {content}')
            if defaultvalue_src_addr:
                child.sendline(
                    f'mt_messaging_cred defaultvalue src_addr {defaultvalue_src_addr}')
            if balance:
                child.sendline(f'mt_messaging_cred quota balance {balance}')
            if early_percent:
                child.sendline(
                    f'mt_messaging_cred quota early_percent {early_percent}')
            if sms_count:
                child.sendline(
                    f'mt_messaging_cred quota sms_count {sms_count}')
            if http_throughput:
                child.sendline(
                    f'mt_messaging_cred quota http_throughput {http_throughput}')
            if smpps_throughput:
                child.sendline(
                    f'mt_messaging_cred quota smpps_throughput {smpps_throughput}')
            if bind is not None:
                child.sendline(f'smpps_cred authorization bind {bind}')
            if max_bindings:
                child.sendline(
                    f'smpps_cred quota max_bindings {max_bindings}')

            child.sendline('ok')

        return self._get_operation_status()

    def remove(self, username: str) -> bool:
        """Remove an user by its uid

        Args:
            username (str): UID of user to remove

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} -r {}'.format(self.__base_cmd__, username))

        return self._get_operation_status()

    def enable(self, username: str) -> bool:
        """Enable an user by it uid

        Args:
            username (str): UID of user to enable

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} -e {}'.format(self.__base_cmd__, username))

        return self._get_operation_status()

    def disable(self, username: str) -> bool:
        """Disable an user by its uid

        Args:
            username (str): UID for user disable

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} -d {}'.format(self.__base_cmd__, username))

        return self._get_operation_status()

    def list(self) -> List[JasminUser]:
        """Get users list

        Returns:
            List[JasminUser]: User list
        """
        global lines
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -l')
            lines = self._parse_list('Total Users:')

        return [JasminUser.from_line(line) for line in lines]

    def inspect(self, uid: str) -> Union[bool, JasminUser]:
        """Get full info on user

        Args:
            uid (str): UID of user to get info on

        Returns:
            JasminUser: A Jasmin user
        """
        global line
        with self.connect() as child:
            child.sendline(f'user -s {uid}')
            line = self._parse_inspect()

        if not line:
            return False

        return JasminUser.from_inspect(line)


class JasminGroupManager(JasminManager):
    __base_cmd__ = 'group'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, gid: str) -> bool:
        """Create a new group

        Args:
            gid (str): Group unique id

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} --add'.format(self.__base_cmd__))
            child.sendline('gid {}'.format(gid))
            child.sendline('ok')

        return self._get_operation_status()

    def inspect(self, id: str):
        pass

    def remove(self, gid: str) -> bool:
        """Remove a group by its id

        Args:
            gid (str): ID of group to remove

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} -r {}'.format(self.__base_cmd__, gid))

        return self._get_operation_status()

    def enable(self, gid: str) -> bool:
        """Enable a group by its id

        Args:
            gid (str): ID of group to enable

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} -e {}'.format(self.__base_cmd__, gid))

        return self._get_operation_status()

    def disable(self, gid: str) -> bool:
        """Disable a group by its id

        Args:
            gid (str): ID of group to disable

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} -d {}'.format(self.__base_cmd__, gid))

        return self._get_operation_status()

    def update(self, *args, **kwargs):
        pass

    def list(self) -> List[JasminGroup]:
        """Get group list

        Returns:
            List`[JasminGroup]: Group list
        """
        global lines
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -l')
            lines = self._parse_list('Total Groups:')

        return [JasminGroup.from_line(line) for line in lines]


class JasminSMPPConnectorManager(JasminManager):
    __base_cmd__ = 'smppccm'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, cid: str, **kwargs) -> bool:
        """Create a new SMPP Connector

        Args:
            cid (str): Unique connector ID
            **kwargs (dict): Additional parameters supported by SMPP Connector

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -a')
            child.expect('')
            child.sendline(f'cid {cid}')
            child.expect('')
            for key, value in kwargs.items():
                child.sendline(f'{key} {value}')
                child.expect('')
            child.sendline('ok')
            child.expect('')

        return self._get_operation_status()

    def update(self, cid: str, **kwargs) -> bool:
        """Update a connector by its id

        Args:
            cid (str): ID of connector to update

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -u {cid}')
            for key, value in kwargs.items():
                child.sendline(f'{key} {value}')
                child.expect('')
            child.sendline('ok')
            child.expect('')

        return self._get_operation_status()

    def remove(self, cid: str) -> bool:
        """REmove a connector  by its ID

        Args:
            cid (str): ID of the connector to remove the

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -r {cid}')
            child.expect('')

        return self._get_operation_status()

    def start(self, cid: str) -> bool:
        """Start a connector by its id

        Args:
            cid (str): ID of  connector to start

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} --start={cid}')
            child.expect('')

        return self._get_operation_status()

    def stop(self, cid: str) -> bool:
        """Stop a connector by its id

        Args:
            cid (str): ID of  connector to start

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} --stop={cid}')
            child.expect('')

        return self._get_operation_status()

    def inspect(self, cid: str) -> Union[JasminSMPPConnector, bool]:
        """Get full info about a connector by its id

        Args:
            cid (str): ID of connector to get info on 

        Returns:
            JasminSMPPConnector: An SMPPConnector
        """
        global line
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -s {cid}')
            line = self._parse_inspect()

        if not line:
            return False

        return JasminSMPPConnector.from_inspect(line)

    def list(self) -> List[JasminSMPPConnector]:
        """List all SMPP Connectors

        Returns:
            List[JasminSMPPConnector]: SMPP connector list
        """
        global lines
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -l')
            lines = self._parse_list('Total connectors:')

        return [JasminSMPPConnector.from_line(line) for line in lines]


class JasminFilterManager(JasminManager):
    __base_cmd__ = 'filter'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, fid: str, type: FilterType, **kwargs) -> bool:
        """Create a new filter

        Args:
            tag (str): Unique filter ID
            type (FilterType): Filter type
            **kwargs (dict): Additional parameters according to filter type 

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} --add')
            child.expect('')
            child.sendline(f'fid {fid}')
            child.expect('')
            child.sendline(f'type {type}')
            child.expect('')
            for key, value in kwargs.items():
                child.sendline(f'{key} {value}')
                child.expect('')
            child.sendline('ok')
            child.expect('')

        return self._get_operation_status()

    def inspect(self, id: str):
        pass

    def remove(self, fid: str) -> bool:
        """Remove a filter by its id

        Args:
            fid (str): ID of filter to remove

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} -r {}'.format(self.__base_cmd__, fid))
            child.expect('')

        return self._get_operation_status()

    def update(self, *args, **kwargs):
        pass

    def list(self) -> List[JasminFilter]:
        """List filters

        Returns:
            List[JasminFilter]: Filter list of
        """
        global lines
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -l')
            lines = self._parse_list('Total Filters:')

        return [JasminFilter.from_line(line) for line in lines]


class JasminMTRouterManager(JasminManager):
    __base_cmd__ = 'mtrouter'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, rate: float, order: int, type: MTRouteType = MTRouteType.DefaultRoute, **kwargs) -> bool:
        """Create a new MT Route

        Args:
            rate (float): Route Rate
            order (int): Route Order
            type (MTRouteType, optional): Route type. Defaults to MTRouteType.DefaultRoute.
            **kwargs (dict): Additional parameters according to route type

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} --add'.format(self.__base_cmd__))
            child.expect('')
            child.sendline(f'type {type}')
            child.expect('')
            for key, value in kwargs.items():
                child.sendline(f'{key} {value}')
                child.expect('')
            child.sendline('rate {}'.format(rate))
            child.expect('')
            child.sendline('order {}'.format(order))
            child.expect('')
            child.sendline('ok')
            child.expect('')

        return self._get_operation_status()

    def remove(self, order: int) -> bool:
        """Remove MT Route using its order

        Args:
            order (int): MT Route order

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline('{} -r {}'.format(self.__base_cmd__, order))
            child.expect('')

        return self._get_operation_status()

    def update(self, *args, **kwargs):
        pass

    def list(self) -> List[JasminMTRoute]:
        """List MT Routes

        Returns:
            List[JasminMTRoute]: MT Routes list
        """
        global lines
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -l')
            lines = self._parse_list('Total MT Routes:')

        return [JasminMTRoute.from_line(line) for line in lines]

    def flush(self) -> bool:
        """Flush MT Routing table. 
        Be careful, this action is UNRECOVERABLE!

        Returns:
            bool: True is operation is successful, otherwise False
        """
        with self.connect() as child:
            child.sendline(f'{self.__base_cmd__} -f')
            child.expect('')

        return self._get_operation_status()

    def inspect(self, id: str):
        pass

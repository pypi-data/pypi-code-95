"""
    An ExoEdge source for interfacing with Modbus TCP devices.
"""
# pylint: disable=I0011,W0312,C0301,C0103,W0123,W1202,C0326,C0111,R0911,R0913,R0914
import sys
import time
import logging
import threading
from os import environ
from .__version__ import __version__
from exoedge_modbus.lib import \
    ExositeModbusTCP, \
    ExositeModbusRTU, \
    ExoEdgeModbusException, \
    REGISTER_NUMBER_MAP
from exoedge.sources import ExoEdgeSource
from exoedge import logger
from murano_client.client import WatchQueue
from pymodbus.exceptions import ModbusException
from pymodbus.constants import Endian

LOG = logger.getLogger(__name__, level=logging.getLogger('exoedge').getEffectiveLevel())

REGISTER_NUMBER_TO_ADDRESS_OFFSET=-1
class ModbusExoEdgeSource(ExoEdgeSource):
    """ Exoedge Modbus source."""

    # EXOEDGE-337 Broken Pipe Error
    # If the client is open too long after the connect() call, the next read will return a "Broken Pipe" error.
    # client.is_socket_open() in theory, should catch this, but doesn't
    # it was found that simply doing a second read mitigates the broken pipe error. Obviously down at the level of wireshark, errors will be seen on the initial read.
    # This is a deeper issue, that could very well have a better solution. The PyModbus library should Ack keep-alives from the PLC.
    def read(self, iteration, register_range, channel):
        try:
            if register_range == "INPUT_COIL":
                response = channel.client.read_discrete_inputs(channel.eval_kwargs)
            if register_range == "HOLDING_COIL":
                response = channel.client.read_coils(channel.eval_kwargs)
            if register_range == "INPUT_REGISTER":
                response = channel.client.read_input_registers(channel.eval_kwargs)
            if register_range == "HOLDING_REGISTER":
                response = channel.client.read_holding_registers(channel.eval_kwargs)
        except:
            if iteration < 2:
                response = self.read(iteration+1, register_range, channel)
            else: raise
        return response

    def run(self):

        modbus_tcp_channels = {e.name: e for e in self.get_channels_by_application("Modbus_TCP")}
        modbus_rtu_channels = {e.name: e for e in self.get_channels_by_application("Modbus_RTU")}

        configured_applications = self.get_configured_applications()
        if modbus_rtu_channels:
            while not configured_applications:
                LOG.critical("Resource 'config_applications' not set for RTU channels.")
                configured_applications = self.get_configured_applications()
                time.sleep(1.0)
        valid_channels = []
        iface_instances = {}
        for channel in modbus_tcp_channels.values():
            ip_address = channel.protocol_config.app_specific_config['ip_address']
            if ip_address not in iface_instances:
                iface_instances.update({
                    ip_address: ExositeModbusTCP(
                        ip_address=channel.protocol_config.app_specific_config['ip_address'],
                        port=int(channel.protocol_config.app_specific_config['port'])
                    )
                })

        for channel in modbus_tcp_channels.values():
            ip_address = channel.protocol_config.app_specific_config['ip_address']
            channel.client = iface_instances.get(ip_address)
            channel.eval_kwargs = {
                'data_address': REGISTER_NUMBER_MAP[
                    channel.protocol_config.app_specific_config['register_range']
                    ]['range'][0] + int(channel.protocol_config.app_specific_config['register']) + REGISTER_NUMBER_TO_ADDRESS_OFFSET,
                'register_count': int(channel.protocol_config.app_specific_config['register_count']),
                'value': None,  # not used/implimented for read operations
                'byte_endianness': channel.protocol_config.app_specific_config['byte_endianness'],
                'register_endianness': channel.protocol_config.app_specific_config['register_endianness'],
                'evaluation_mode': channel.protocol_config.app_specific_config['evaluation_mode'],
                'bitmask': channel.protocol_config.app_specific_config['bitmask'],
            }
            valid_channels.append(channel)
            LOG.critical("channel.eval_kwargs: {!r}".format(channel.eval_kwargs))

        applications = configured_applications.get('applications') if configured_applications else {}
        modbus_rtu_applications = applications.get('Modbus_RTU', {}) if applications else {}

        for iface in modbus_rtu_applications.get("interfaces", []):
            for channel in modbus_rtu_channels.values():
                interface = iface.get("interface")
                if interface == channel.protocol_config.interface and interface not in iface_instances:
                    iface_instances.update({interface: ExositeModbusRTU(**iface)})

        for channel in modbus_rtu_channels.values():
            if channel.protocol_config.interface not in iface_instances:
                channel.put_channel_error("config_applications not configured for Modbus_RTU")
                continue
            channel.client = iface_instances.get(channel.protocol_config.interface)
            channel.eval_kwargs = {
                'data_address': REGISTER_NUMBER_MAP[
                    channel.protocol_config.app_specific_config['register_range']
                    ]['range'][0] + int(channel.protocol_config.app_specific_config['register']) + REGISTER_NUMBER_TO_ADDRESS_OFFSET,
                'register_count': int(channel.protocol_config.app_specific_config['register_count']),
                'value': None,  # not used/implimented for read operations
                'byte_endianness': channel.protocol_config.app_specific_config['byte_endianness'],
                'register_endianness': channel.protocol_config.app_specific_config['register_endianness'],
                'evaluation_mode': channel.protocol_config.app_specific_config['evaluation_mode'],
                'bitmask': channel.protocol_config.app_specific_config['bitmask'],
            }
            valid_channels.append(channel)
            LOG.critical("channel.eval_kwargs: {!r}".format(channel.eval_kwargs))


        while not self.is_stopped():

            while not self._Q_DATA_OUT.empty():
                data_out_obj = self._Q_DATA_OUT.safe_get(timeout=0.1)
                LOG.info("GOT DATA_OUT: {}".format(data_out_obj))
                if data_out_obj:
                    channel = data_out_obj.channel
                    LOG.critical(
                        "Processing modbus data out: {}({}): {}"
                        .format(
                            channel.name,
                            channel.eval_kwargs['data_address'],
                            data_out_obj.data_out_value)
                    )
                    register_range = channel.protocol_config.app_specific_config['register_range']
                    response = None

                    if register_range in ["INPUT_COIL", "HOLDING_COIL"]:
                        try:
                            channel.eval_kwargs['value'] = data_out_obj.data_out_value
                            response = channel.client.write_coil(
                                channel.eval_kwargs['data_address'],
                                data_out_obj.data_out_value
                            )
                            LOG.warning(
                                "WRITE COIL RESPONSE: {}".format(response))
                        except ModbusException as exc:
                            LOG.exception("INPUT_COIL Write Exception".format(format_exc=exc))
                            channel.put_channel_error(exc)
                        except ExoEdgeModbusException as exc:
                            LOG.exception("INPUT_COIL Write EXCEPTION")
                            channel.put_channel_error(exc)
                        except Exception as exc:
                            LOG.exception("INPUT_COIL Write EXCEPTION")
                            channel.put_channel_error(exc)

                        # cleanup
                        channel.eval_kwargs['value'] = None

                    elif register_range in ["INPUT_REGISTER", "HOLDING_REGISTER"]:
                        try:
                            channel.eval_kwargs['value'] = data_out_obj.data_out_value
                            response = channel.client.write_registers(
                                channel.eval_kwargs['data_address'],
                                channel.eval_kwargs['register_count'],
                                str(channel.eval_kwargs['value']), # Cast to string because method expects csv
                                channel.eval_kwargs['evaluation_mode'],
                                channel.eval_kwargs['byte_endianness'],
                                channel.eval_kwargs['register_endianness']
                            )
                        except ModbusException as exc:
                            LOG.exception("HOLDING_REGISTER Exception".format(format_exc=exc))
                            channel.put_channel_error(exc)
                        except ExoEdgeModbusException as exc:
                            LOG.exception("HOLDING_REGISTER EXCEPTION")
                            channel.put_channel_error(exc)
                        except Exception as exc:
                            LOG.exception("HOLDING_REGISTER General exception".format(format_exc=exc))
                            channel.put_channel_error(exc)

                        # cleanup
                        channel.eval_kwargs['value'] = None

            for channel in valid_channels:
                if channel.is_sample_time():
                    try:
                        channel.client.slave_id = int(channel.protocol_config.app_specific_config.get('slave_id', 1))
                    except ValueError as exc:
                        LOG.critical("ValueError Exception: {} - setting slave_id to 1".format(exc))
                        channel.client.slave_id = 1

                    LOG.info("POLLING MODBUS CHANNEL: {}".format(channel.name))
                    register_range = channel.protocol_config.app_specific_config['register_range']
                    response = None

                    if register_range == "INPUT_COIL":
                        try:
                            response = self.read(0, register_range, channel)
                        except ModbusException as exc:
                            LOG.exception("INPUT_COIL Exception".format(format_exc=exc))
                            channel.put_channel_error(exc)
                        except ExoEdgeModbusException as exc:
                            LOG.exception("INPUT_COIL EXCEPTION")
                            channel.put_channel_error(exc)
                        except Exception as exc:
                            LOG.exception("INPUT_COIL EXCEPTION")
                            channel.put_channel_error(exc)

                    elif register_range == "HOLDING_COIL":
                        try:
                            response = self.read(0, register_range, channel)
                        except ModbusException as exc:
                            LOG.exception("HOLDING_COIL Exception".format(format_exc=exc))
                            channel.put_channel_error(exc)
                        except ExoEdgeModbusException as exc:
                            LOG.exception("HOLDING_COIL EXCEPTION")
                            channel.put_channel_error(exc)
                        except Exception as exc:
                            LOG.exception("HOLDING_COIL General exception".format(format_exc=exc))
                            channel.put_channel_error(exc)

                    elif register_range == "INPUT_REGISTER":
                        try:
                            response = self.read(0, register_range, channel)
                        except ModbusException as exc:
                            LOG.exception("INPUT_REGISTER Exception".format(format_exc=exc))
                            channel.put_channel_error(exc)
                        except ExoEdgeModbusException as exc:
                            LOG.exception("INPUT_REGISTER EXCEPTION")
                            channel.put_channel_error(exc)
                        except Exception as exc:
                            LOG.exception("INPUT_REGISTER General exception".format(format_exc=exc))
                            channel.put_channel_error(exc)

                    elif register_range == "HOLDING_REGISTER":
                        try:
                            response = self.read(0, register_range, channel)
                        except ModbusException as exc:
                            LOG.exception("HOLDING_REGISTER Exception".format(format_exc=exc))
                            channel.put_channel_error(exc)
                        except ExoEdgeModbusException as exc:
                            LOG.exception("HOLDING_REGISTER EXCEPTION")
                            channel.put_channel_error(exc)
                        except Exception as exc:
                            LOG.exception("HOLDING_REGISTER General exception".format(format_exc=exc))
                            channel.put_channel_error(exc)

                    if response is not None:
                        channel.put_sample(response)
                    LOG.debug("sleeping 0.01 sec after modbus read.")
                    time.sleep(0.01)
                LOG.debug("sleeping 0.01 sec after sweeping all channels.")
                time.sleep(0.01)

        for channel in valid_channels:
            LOG.critical(
                "Closing client: {} :: {}"
                .format(channel, dir(channel.client))
            )
            channel.client.client.close()
        LOG.critical("{} HAS BEEN STOPPED.".format(self.name))


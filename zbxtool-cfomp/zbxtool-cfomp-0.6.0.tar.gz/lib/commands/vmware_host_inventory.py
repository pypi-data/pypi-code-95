#!/bin/env python3
# coding:utf-8

"""
从vCenter中获取esxi主机信息，更新到Zabbix inventory
"""
import sys
import argparse
import logging
from urllib.parse import urlparse
from pyVmomi import vim
from pyVim.connect import Disconnect, SmartConnectNoSSL
from infi.pyvmomi_wrapper.esxcli import EsxCLI

parser = argparse.ArgumentParser("Correct discoverd host name")
parser.set_defaults(handler=lambda args: main(args))


def fetch_esxi(host, user, pwd, esxi_name, port=443):
    '''
    通过 pyVmomi 模块读取 vCenter 中 esxi server的信息。
    '''
    si = SmartConnectNoSSL(host=host, user=user, pwd=pwd, port=port)
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem, vim.Datacenter], True)

    # vcenter自定义的属性, 取系统中对应的字段的key, {'机柜': 43, '机房名称': 44}
    custom_key = {'机柜':'', '机房名称':''}

    cfm = content.customFieldsManager
    for field in cfm.field:
        if field.name in custom_key.keys():
            custom_key[field.name] = field.key

    esxi_info = {}

    # 取数据中心的机房名称
    for view in container.view:
        if not isinstance(view, vim.Datacenter):
            continue

        # esxi 属于某 datacenter, 则取 datacenter 自定义属性
        for child in view.hostFolder.childEntity:

            isFind = False  #是否在该 datacenter 找到目标 esxi

            # 子节点是 ClusterCompute, esxi 挂在 ClusterCompute下面
            if isinstance(child, vim.ClusterComputeResource):
                for host in child.host:
                    if esxi_name == host.name:
                        isFind = True
            else:
            # esxi 直接挂在 datacenter 下
                if esxi_name == child.name:
                    isFind = True

            if isFind:
                # location 默认值为datacenter的名字 
                esxi_info['location'] = view.name
                # 如果datacenter有“机房名称”自定义属性，则覆盖前者。
                for prop in view.customValue:
                    if prop.key == custom_key['机房名称']:
                        esxi_info['location'] = prop.value
                        break

    # 取esxi属性
    for esxi_ in container.view:
        if esxi_.name != esxi_name:
            continue
        esxi_info['type'] = 'Server'
        esxi_info['name'] = esxi_.name
        esxi_info['os'] = esxi_.config.product.name
        esxi_info['os_full'] = esxi_.summary.config.product.fullName
        esxi_info['os_short'] = esxi_.config.product.osType
        esxi_info['tag'] = 'Esxi'
        esxi_info['model'] = esxi_.summary.hardware.model
        esxi_info['vendor'] = esxi_.summary.hardware.vendor
        esxi_info['management_ip'] = esxi_.summary.managementServerIp
        esxi_info['cpu'] = '(%s) * %s  %s核  %s线程' % (esxi_.summary.hardware.cpuModel,
                           esxi_.summary.hardware.numCpuPkgs,
                           esxi_.summary.hardware.numCpuCores,
                           esxi_.summary.hardware.numCpuThreads)
        esxi_info['mem'] = f'内存: {esxi_.summary.hardware.memorySize/1024/1024//1024}GB'
        # get host's ipA and netmask
        for vnic in esxi_.config.network.vnic:
            if isinstance(vnic, vim.host.VirtualNic):
                esxi_info['ip'] = vnic.spec.ip.ipAddress
                esxi_info['subnet_mask'] = vnic.spec.ip.subnetMask
        # get host's mac address
        for portgroup in esxi_.config.network.portgroup:
            for port in portgroup.port:
                if port.type == 'host':
                    esxi_info['mac_address'] = ''.join(port.mac)
        # get host's serial_number
        ordered_keys = ['SerialNumberTag', 'EnclosureSerialNumberTag', 'ServiceTag']
        for iden in esxi_.summary.hardware.otherIdentifyingInfo:
            if isinstance(iden, vim.host.SystemIdentificationInfo) and iden.identifierType.key in ordered_keys:
                esxi_info[iden.identifierType.key] = iden.identifierValue

        for key in ordered_keys:
            if esxi_info.get(key):
                esxi_info['serial_number'] = esxi_info.get(key)
                break

        if not esxi_info.get('serial_number'):
            cli = EsxCLI(esxi_)
            hardware = cli.get("hardware.platform")
            esxi_info['serial_number'] = hardware.Get().SerialNumber


        # 取机柜名称
        esxi_info['site_rack'] = None
        for prop in esxi_.customValue:
            if prop.key == custom_key['机柜']:
                esxi_info['site_rack'] = prop.value
                break

    Disconnect(si)
    return esxi_info


def main(args):
    '''
    更新 zabbix 中 Hypervisors 组中 host 的 inventory. 其内容从 vCenter 中获取.
    '''
    zapi = args.zapi
    
    zbx_group = zapi.hostgroup.get({
        'output': ['groupid', 'name'],
        'selectHosts': ['hostid', 'name'],
        'filter': {'name': 'Hypervisors'}
    })

    if not zbx_group:
        sys.exit()

    hosts = zbx_group[0].get('hosts')
    macros = {}

    tmp_ = zapi.host.get({
        'output': ['hostid', 'name'],
        'hostids': [h.get('hostid') for h in hosts],
        'selectMacros': 'extend'
    })
    for host_ in tmp_:
        macros[host_['name']] = {}
        for ma_ in host_.get('macros'):
            macros[host_['name']][ma_.get('macro')] = ma_.get('value')

    for host in hosts:
        host_id = host.get('hostid')
        host_name = host.get('name')
        vcenter_ip = urlparse(macros[host_name].get('{$URL}')).hostname
        vcenter_admin = macros[host_name].get('{$USERNAME}')
        vcenter_pwd = macros[host_name].get('{$PASSWORD}')

        logging.debug(f'[fetch_esxi] vcenter_ip: {vcenter_ip}, esxi_name:{host_name}')
        esxi_info = fetch_esxi(host=vcenter_ip,
                               user=vcenter_admin,
                               pwd=vcenter_pwd,
                               esxi_name=host_name)

        zapi.host.update({
            "hostid": host_id,
            "inventory": {
                "type": esxi_info.get('type'),
                "name": esxi_info.get('name'),
                "alias": esxi_info.get('ip'),
                "os": esxi_info.get('os'),
                "os_full": esxi_info.get('os_full'),
                "os_short": esxi_info.get('os_short'),
                "serialno_a": esxi_info.get('serial_number'),
                "tag": esxi_info.get('tag'),
                "macaddress_a": esxi_info.get('mac_address'),
                "macaddress_b": esxi_info.get('mac_address'),
                "model": esxi_info.get('model'),
                "vendor": esxi_info.get('vendor'),
                "host_networks": esxi_info.get('ip'),
                "host_netmask": esxi_info.get('subnet_mask'),
                "hardware_full": '\n'.join([esxi_info.get('cpu',''), esxi_info.get('mem','')]),
                "location": esxi_info.get('location'),
                "site_rack": esxi_info.get('site_rack')
            }
        })
        logging.info(f'update host->{host_name} success!')

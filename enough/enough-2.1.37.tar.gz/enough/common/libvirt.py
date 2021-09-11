import libvirt
import logging
import os
import sh
import textwrap

from enough.common.ssh import SSH
from enough.common import ansible_utils
from enough.common.dotenough import Hosts
from enough.common import retry

log = logging.getLogger(__name__)


def libvirt_install(config_dir, share_dir, **kwargs):
    Hosts(config_dir).create_or_update('libvirt-hypervisor', kwargs['host'], '22')
    playbook = ansible_utils.Playbook(config_dir, share_dir)
    playbook.run('--private-key', f'{config_dir}/infrastructure_key',
                 '--limit', 'libvirt-hypervisor,localhost',
                 '--extra-vars', f'vpn={kwargs.get("vpn","NOOP")}',
                 f'{share_dir}/playbooks/libvirt-hypervisor/libvirt-hypervisor-playbook.yml')
    return True


class Libvirt(object):

    BIND_MAC = '52:54:00:00:00:02'
    NETWORK = {
        'external': {
            'prefix': '10.23.10',
            'name': 'enough-ext',
        },
        'internal': {
            'prefix': '10.23.90',
            'name': 'enough-int',
        },
    }

    def __init__(self, config_dir, share_dir, **kwargs):
        self.args = kwargs
        self.config_dir = config_dir
        self.share_dir = share_dir
        self.cnx = None
        self.ansible = ansible_utils.Ansible(self.config_dir, self.share_dir,
                                             self.args.get('inventory'))
        self.domain = kwargs.get('domain', 'enough.community')
        self.images_dir = f'/var/lib/libvirt/images/enough/{self.domain}'
        self.network_definitions = None

    def lv(self):
        if self.cnx is None:
            self.cnx = libvirt.open('qemu:///system')
        return self.cnx

    def host_image_name(self, name):
        return f'{self.images_dir}/{name}.qcow2'

    def host_snapshot_name(self, name):
        return f'{self.images_dir}/{name}-snapshot.qcow2'

    def public_key(self):
        return f'{self.config_dir}/infrastructure_key.pub'

    def sysprep(self, name, definition):
        fqdn = f'{name}.{self.domain}'
        sh.virt_sysprep(
            '-a', self.host_image_name(name),
            '--enable', 'customize',
            '--no-network',
            '--hostname', fqdn,
            '--run-command', f'sed -i -e "s/^127.0.1.1.*/127.0.1.1 {fqdn}/" /etc/hosts',
            '--ssh-inject', f'debian:file:{self.public_key()}',
            '--copy-in', f'{self.share_dir}/playbooks/infrastructure/network.sh:/root',
            '--firstboot-command', ('env '
                                    f'PORT={definition["port"]} '
                                    f'ROUTED={definition["network_interface_routed"]} '
                                    f'NOT_ROUTED={definition["network_interface_not_routed"]} '
                                    f'UNCONFIGURED={definition["network_interface_unconfigured"]} '
                                    'bash -x /root/network.sh'),
        )

    def resize(self, name, definition):
        sh.qemu_img.create('-f', 'qcow2', '-o', 'preallocation=metadata',
                           self.host_image_name(name), definition['disk'])
        sh.virt_resize(
            '--expand', '/dev/sda1',
            self.image_name(),
            self.host_image_name(name))

    def get(self, name):
        try:
            return self.lv().lookupByName(name)
        except libvirt.libvirtError:
            return None

    def _create_or_update(self, definition):
        name = definition['name']
        if self.get(name) is not None:
            info = {
                'ipv4': self.get_ipv4(name),
                'port': definition['port'],
            }
            Hosts(self.config_dir).create_or_update(
                definition['name'], info['ipv4'], info['port'])
            return info
        log.info(f"{name}: building image")
        self.image_builder()
        log.info(f"{name}: copy and resize image")
        self.resize(name, definition)
        log.info(f"{name}: preparing image")
        self.sysprep(name, definition)
        log.info(f"{name}: creating host")
        sh.env('HOME=/tmp',
               'virt-install',
               '--connect', 'qemu:///system',
               '--network', f"network={definition['network-external']}{definition['mac']}",
               '--network', f"network={definition['network-internal']}",
               '--boot', 'hd',
               '--name', name,
               '--memory', definition['ram'],
               '--vcpus',  definition['cpus'],
               '--cpu', 'host',
               '--disk', f'path={self.host_image_name(name)},bus=virtio,format=qcow2',
               '--os-type=linux',
               '--os-variant=debian10',
               '--graphics', 'none',
               '--noautoconsole')
        log.info(f"{name}: waiting for ipv4 to be allocated")
        info = {
            'ipv4': self.get_ipv4(name),
            'port': definition['port'],
        }
        log.info(f"{name}: waiting for {info['ipv4']}:{info['port']} to come up")
        SSH.wait_for_ssh(info['ipv4'], info['port'])
        Hosts(self.config_dir).create_or_update(
            definition['name'], info['ipv4'], info['port'])
        log.info(f"{name}: host is ready")
        return info

    @retry.retry((libvirt.libvirtError, AssertionError), 8)
    def get_ipv4(self, name):
        dom = self.lv().lookupByName(name)
        ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
        assert ifaces, f'interfaceAddresses returned {ifaces}'
        for (name, val) in ifaces.items():
            addrs = val['addrs']
            assert len(addrs) == 1, f"{addrs} expected len is 1"
            addr = val['addrs'][0]
            assert addr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4
            return addr['addr']

    def create_or_update(self, names):
        self.networks_create()
        definitions = self.get_definitions()
        r = {}
        for name in names:
            r[name] = self._create_or_update(
                self.get_definition(name, definitions[name]))
        return r

    def get_definitions(self):
        return self.ansible.get_hostvars(variable=None)

    def get_definition(self, name, definition):
        r = {}
        #
        # This hardcoded MAC is convenient for testing purposes.
        # It helps to have a fixed IP for the bind server. It
        # is not a requirement.
        #
        if name == 'bind-host':
            r['mac'] = f',mac={Libvirt.BIND_MAC}'
        else:
            r['mac'] = ''
        for network in ('external', 'internal'):
            r[f'network-{network}'] = definition.get(
                    f'libvirt_network_{network}_name',
                    Libvirt.NETWORK[network]['name'],
                )
        r.update({
            'name': name,
            'port': definition.get('ansible_port', '22'),
            'ram': definition.get('libvirt_ram', '2048'),
            'cpus': definition.get('libvirt_cpus', '1'),
            'disk': definition.get('libvirt_disk', '20G'),
            'network_interface_unconfigured': definition.get('network_interface_unconfigured'),
            'network_interface_routed': definition.get('network_interface_routed'),
            'network_interface_not_routed': definition.get('network_interface_not_routed'),
        })
        return r

    @staticmethod
    def _image_name():
        return 'debian-10.qcow2'

    def image_name(self):
        return f'{self.images_dir}/{self._image_name()}'

    @staticmethod
    def _image_builder(image):
        if os.path.exists(image):
            return False
        sh.virt_builder(
            'debian-10',
            '--no-cache',
            '--output', image,
            '--format', 'qcow2',
            '--size', '6G',
            '--install', 'sudo',
            '--root-password', 'disabled',
            '--run-command', 'dpkg-reconfigure --frontend=noninteractive openssh-server',
            '--run-command', ('useradd -s /bin/bash -m debian || true ; '
                              'echo "debian ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-debian'),
        )
        sh.chmod('0660', image)
        sh.chgrp('libvirt', image)
        return True

    def image_dir_ensure(self):
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
        sh.chmod('0771', self.images_dir)
        sh.chgrp('libvirt', self.images_dir)

    def image_builder(self):
        self.image_dir_ensure()
        return self._image_builder(self.image_name())

    def networks_definitions_get(self):
        if self.network_definitions:
            return self.network_definitions

        variables = ('libvirt_network_external_prefix',
                     'libvirt_network_internal_prefix',
                     'libvirt_network_external_name',
                     'libvirt_network_internal_name')
        variables = "{%s}" % ', '.join(f'"{x}": {x}' for x in variables)
        network_vars = self.ansible.get_global_variable(variables)
        d = {}
        for network in ('external', 'internal'):
            vars = {}
            for var in ('prefix', 'name'):
                vars[var] = network_vars.get(
                    f'libvirt_network_{network}_{var}',
                    Libvirt.NETWORK[network][var],
                )
            d[network] = vars
        self.network_definitions = d
        return self.network_definitions

    def networks_create(self):
        r = []
        d = self.networks_definitions_get()
        for network in ('external', 'internal'):
            vars = d[network]
            r.append(self.network_create(vars['name'], vars['prefix']))
            if network == 'external':
                self.network_host_set(vars['name'],
                                      'bind-host',
                                      Libvirt.BIND_MAC,
                                      f'{vars["prefix"]}.2')
        return r

    def networks_destroy(self):
        for (_, network) in self.networks_definitions_get().items():
            self.network_destroy(network['name'])

    def network_host_definition(self, host, mac, ip):
        return f"<host mac='{mac}' name='{host}' ip='{ip}'/>"

    def network_host_set(self, name, host, mac, ip):
        network = self.lv().networkLookupByName(name)
        xml = self.network_host_definition(host, mac, ip)
        if xml in network.XMLDesc():
            return False
        network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_LAST,
                       libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST,
                       -1,
                       xml,
                       (libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE |
                        libvirt.VIR_NETWORK_UPDATE_AFFECT_CONFIG))
        return True

    def network_host_unset(self, name, host, mac, ip):
        network = self.lv().networkLookupByName(name)
        xml = self.network_host_definition(host, mac, ip)
        if xml not in network.XMLDesc():
            return False
        network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE,
                       libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST,
                       -1,
                       xml,
                       (libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE |
                        libvirt.VIR_NETWORK_UPDATE_AFFECT_CONFIG))
        return True

    def network_create(self, name, prefix):
        if name not in self.lv().listNetworks():
            network = textwrap.dedent(f"""
            <network>
              <name>{name}</name>
              <forward mode='nat'/>
              <bridge name='virbr{name}' stp='on' delay='0'/>
              <ip address='{prefix}.1' netmask='255.255.255.0'>
                <dhcp>
                  <range start='{prefix}.100' end='{prefix}.254'/>
                </dhcp>
              </ip>
            </network>
            """)
            network = self.lv().networkDefineXML(network)
            network.create()
            network.autostart()
        else:
            network = self.lv().networkLookupByName(name)
        return network

    def network_destroy(self, name):
        if name in self.lv().listNetworks():
            network = self.lv().networkLookupByName(name)
            network.destroy()
            network.undefine()
            return True
        else:
            return False

    def delete(self, name):
        domain = self.get(name)
        if domain:
            domain.destroy()
            domain.undefine()
        Hosts(self.config_dir).delete(name)
        return domain is not None

    def destroy_everything(self, prefix):
        for domain in self.lv().listAllDomains():
            if prefix in domain.name():
                self.delete(domain.name())
        for network in self.lv().listNetworks():
            if prefix in network:
                self.network_destroy(network)

    def pets_get(self):
        return self.ansible.get_global_variable('libvirt_pets')

    @retry.retry(sh.ErrorReturnCode_1, 13)
    def backup_create_pet_upload(self, openstack, pet):
        pathname = self.host_image_name(pet)
        log.info(f"backup upload {pathname} to {pet}")
        openstack.image_backup_upload(pet, pathname)

    def backup_snapshot_create(self, pet):
        self.backup_snapshot_remove(pet)
        sh.virsh('--connect', 'qemu:///system',
                 'snapshot-create-as', '--domain', pet, 'enough-backup-state',
                 '--diskspec', f'vda,file={self.host_snapshot_name(pet)}',
                 '--disk-only', '--atomic')

    def backup_snapshot_remove(self, pet):
        if os.path.exists(self.host_snapshot_name(pet)):
            sh.virsh('--connect', 'qemu:///system', 'blockcommit',
                     '--domain', pet, '--path', 'vda',
                     '--delete', '--active', '--verbose', '--pivot')
            sh.virsh('--connect', 'qemu:///system', 'snapshot-delete',
                     '--domain', pet, '--metadata', '--snapshotname', 'enough-backup-state')

    def backup_create_pet(self, openstack, pet):
        self.backup_snapshot_create(pet)
        try:
            self.backup_create_pet_upload(openstack, pet)
        finally:
            self.backup_snapshot_remove(pet)

    def backup_create(self, openstack):
        log.info(f"pets {self.pets_get()}")
        for pet in self.pets_get():
            self.backup_create_pet(openstack, pet)

    def backup_prune(self, openstack):
        openstack.image_backup_prune(self.pets_get(), self.args['days'])

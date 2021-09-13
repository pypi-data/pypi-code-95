from collections.abc import Collection, Iterable
from ipaddress import IPv4Address, IPv4Network
from typing import Union


class IPv4TreeNode(Iterable):
    def __init__(self, key: Union[int, str],
                 prefixlen: int,
                 size: int = 1,
                 parent: Union['IPv4TreeNode', None] = None,
                 islast: bool = False):
        if parent is not None:
            parent.new_child(key, self)
        self._parent = parent
        self._children = [None, None]
        self._prefixlen = prefixlen
        self._prefix = "".join([parent.prefix, str(key)]) if parent is not None else str(key)
        self._size = size
        self._islast = islast

    @property
    def parent(self) -> 'IPv4TreeNode':
        return self._parent

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def prefixlen(self) -> int:
        return self._prefixlen

    def child(self, key: Union[int, str]) -> Union['IPv4TreeNode', None]:
        return self._children[int(key)]

    @property
    def children(self) -> list:
        return self._children

    def new_child(self, key: Union[int, str], node: Union['IPv4TreeNode', None]) -> None:
        self._children[int(key)] = node

    def update(self, prefixlen: int, size: int = 1) -> None:
        self._size += size
        if prefixlen > self._prefixlen:
            self._islast = True

    def fullness(self) -> float:
        if self._prefixlen == 32:
            return 1.0
        if self._prefixlen == 31:
            return self._size / 2.0
        return self._size / (2.0 ** (32 - self._prefixlen))

    def __repr__(self) -> str:
        return str(self)

    def true_last_node(self):
        return self._children[0] is None and self._children[1] is None

    def aggregate(self, fullness: Union[int, float]) -> None:
        if self.fullness() >= fullness:
            self._islast = True

    def __iter__(self) -> Iterable:
        yield self
        if not self._islast:
            for child in self._children:
                if child is not None:
                    yield from iter(child)

    def __int__(self) -> int:
        from copy import deepcopy
        s = deepcopy(self._prefix)
        for _ in range(32 - self._prefixlen):
            s = "".join([s, "0"])
        return int(s, 2)

    def __str__(self) -> str:
        if self._prefixlen > 0:
            return "/".join([str(IPv4Address(int(self))),
                             str(self._prefixlen)])
        return "root"

    def _is_root(self) -> bool:
        return "root" == str(self)

    def network_address(self) -> IPv4Address:
        return IPv4Address(str(self).split('/')[0])

    @property
    def size(self) -> int:
        return self._size

    @property
    def islast(self) -> bool:
        return self._islast


class IPv4Tree(Collection):
    def __init__(self) -> 'IPv4Tree':
        self._root = IPv4TreeNode(key=0,
                                  prefixlen=0,
                                  size=0)
        self._nodes = 1
        self._nodes_map = {}

    def _insert_node(self, prev: IPv4TreeNode, key: Union[int, str], size: int = 1, **kwargs) -> IPv4TreeNode:
        node = IPv4TreeNode(key=key,
                            prefixlen=prev.prefixlen + 1,
                            size=size,
                            parent=prev)
        self._nodes += 1
        return node

    def delete(self, ip: Union[str, int, IPv4Address, IPv4Network]) -> None:
        net = IPv4Network(ip)
        if not self.intree(ip):
            raise ValueError('Network {} not in tree'.format(str(net)))

        size = net.num_addresses
        node = self._root
        prev = node
        in_last = False
        for n in _get_binary_path_from_ipv4_addr(net):
            prev = node
            node = prev.child(n)
            inv_key = '1' if n == '0' else '0'
            inv_node = prev.child(inv_key)
            if prev.islast and not in_last:
                in_last = True

            if node == None:
                node = self._insert_node(prev, n, 0)

            if inv_node == None:
                inv_node = self._insert_node(prev, inv_key, 0)
                inv_node._islast = in_last

            prev._islast = False
            if node.prefixlen == net.prefixlen:
                break

        prev.new_child(n, None)
        if prev.true_last_node():
            prev._islast = True

        while prev is not None:
            prev.update(-1, -size)
            prev = prev.parent

    def intree(self, ip: Union[str, int, IPv4Address, IPv4Network]) -> bool:
        ip = IPv4Network(ip)
        intree = ip in self
        if intree:
            return True
        node = self._root
        for n in _get_binary_path_from_ipv4_addr(ip):
            prev = node
            node = prev.child(n)
            if node is None:
                return False
            if node.islast or node.prefixlen == ip.prefixlen:
                break
        return True

    def insert(self, ip: Union[str, int, IPv4Address, IPv4Network], **kwargs) -> None:
        ip = IPv4Network(ip)
        intree = ip in self
        if intree:
            return

        size = ip.num_addresses
        node = self._root
        self._root.update(-1, size)
        was_insert = False
        for n in _get_binary_path_from_ipv4_addr(ip):
            prev = node
            node = prev.child(n)
            if node is None:
                node = self._insert_node(prev, n, size, **kwargs)
                was_insert = True
            else:
                node.update(node.prefixlen, size)

            if node.islast:
                # try insert for subnetwork of exist in tree
                break

            if node.prefixlen == ip.prefixlen:
                # try insert for supernetwork?
                break

        node._islast = True
        if not was_insert:
            if node.prefixlen != ip.prefixlen:
                # is supernet
                excess = size
            else:
                excess = node.size - size
            while node is not None:
                node.update(-1, -excess)
                node = node.parent
        else:
            # new node in last level
            self._nodes_map[ip] = node

    def __contains__(self, ipv4: Union[str, int, IPv4Address, IPv4Network]) -> bool:
        return IPv4Network(ipv4) in self._nodes_map.keys()

    def __iter__(self) -> Iterable:
        return iter(self._root)

    def __len__(self) -> int:
        return self._root.size

    def __getitem__(self, ipv4: Union[str, int, IPv4Address, IPv4Network]) -> IPv4TreeNode:
        net = IPv4Network(ipv4)
        node = self._root
        for n in _get_binary_path_from_ipv4_addr(net):
            node = node.child(n)
            if node is None or node.prefixlen == net.prefixlen:
                break
        return node

    def aggregate(self, fullness: Union[int, float]) -> None:
        for node in self:
            node.aggregate(fullness)

    def last_assignment(self, prefixlen: int = 32, islast: bool = False) -> None:
        """
        Default values undo 'aggregate' method
        """
        for node in self:
            if node.prefixlen < prefixlen:
                node._islast = islast

    def __repr__(self) -> str:
        prefixlens = {}
        last_nodes = 0
        for node in self:
            prefixlen = str(node.prefixlen)
            if prefixlen not in prefixlens.keys():
                prefixlens[prefixlen] = 1
            else:
                prefixlens[prefixlen] += 1
            if node.islast():
                last_nodes += 1
        return str(prefixlens) + "\nTotal nodes: {}\nSize: {}" \
                                 "\nLast nodes: {}".format(self._nodes,
                                                           self._root.size,
                                                           last_nodes)


def _get_binary_path_from_ipv4_addr(ipv4: Union[IPv4Address, IPv4Network]):
    if isinstance(ipv4, IPv4Network):
        return "{0:032b}".format(int(ipv4.network_address))
    if isinstance(ipv4, IPv4Address):
        return "{0:032b}".format(int(ipv4))
    raise TypeError("bad type {}".format(type(ipv4)))

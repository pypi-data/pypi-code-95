"""
This library is for holding SLURM.conf node types and option data
"""


class NodeType:
    def __init__(self):
        self.allow_groups = None
        self.allow_users = None
        self.bcast_addr = None
        self.boards = None
        self.cores_spec_count = None
        self.cores_per_socket = None
        self.cpu_bind = None
        self.cpus = None
        self.cpus_spec_list = None
        self.deny_groups = None
        self.deny_users = None
        self.features = None
        self.frontend_name = None
        self.frontend_addr = None
        self.gres = None
        self.mem_spec_limit = None
        self.node_addr = None
        self.node_hostname = None
        self.node_name = None
        self.port = None
        self.procs = None
        self.real_Memory = None
        self.reason = None
        self.sockets = None
        self.sockets_per_board = None
        self.state = None
        self.threads_per_core = None
        self.tmp_disk = None
        self.tres_weights = None
        self.weight = None

    def __str__(self):
        return """node: {}( allow_groups:{}, allow_users:{}, bcast_addr:{},
        boards:{}, cores_spec_count:{}, cores_per_socket:{}, cpu_bind:{},
        cpus:{}, cpus_spec_list:{}, deny_groups:{}, deny_users:{},
        features:{}, frontend_name:{}, frontend_addr:{}, gres:{},
        mem_spec_limit:{}, node_addr:{}, node_hostname:{},
        port:{}, procs:{}, real_Memory:{}, reason:{}, sockets:{},
        sockets_per_board:{}, state:{}, threads_per_core:{}, tmp_disk:{},
        tres_weights:{}, weight:{})""".format(
            self.node_name,
            self.allow_groups,
            self.allow_users,
            self.bcast_addr,
            self.boards,
            self.cores_spec_count,
            self.cores_per_socket,
            self.cpu_bind,
            self.cpus,
            self.cpus_spec_list,
            self.deny_groups,
            self.deny_users,
            self.features,
            self.frontend_name,
            self.frontend_addr,
            self.gres,
            self.mem_spec_limit,
            self.node_addr,
            self.node_hostname,
            self.port,
            self.procs,
            self.real_Memory,
            self.reason,
            self.sockets,
            self.sockets_per_board,
            self.state,
            self.threads_per_core,
            self.tmp_disk,
            self.tres_weights,
            self.weight)

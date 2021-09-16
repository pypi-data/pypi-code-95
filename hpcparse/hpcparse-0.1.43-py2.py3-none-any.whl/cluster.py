class Cluster:
    def __init__(self):
        self.name = None
        self.control_host = None
        self.control_port = None
        self.rpc = None
        self.share = None
        self.group_jobs = None
        self.group_tres = None
        self.group_submit = None
        self.max_jobs = None
        self.max_tres = None
        self.max_submit = None
        self.max_wall = None
        self.qos = None
        self.def_qos = None

    def __str__(self):
        return """Cluster paramaters (Name: {}, Control Host: {},
        Control Port: {}, RPC: {}, Share: {}, Group Jobs: {}, Group TRES: {},
        Group Submit: {}, Max Jbs: {}, Max TRES: {}, Max Submit: {},
        max_wall{}, QOS: {}, def_qos: {},"""\
        .format(self.name, self.control_host, self.control_port, self.rpc,
                self.partition, self.share, self.group_jobs, self.group_tres,
                self.group_submit, self.max_jobs, self.max_tres,
                self.max_submit, self.qos, self.def_qos)

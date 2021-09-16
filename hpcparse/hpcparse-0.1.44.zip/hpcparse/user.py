class User:
    def __init__(self):
        self.username = None
        self.def_account = None
        self.admin = None
        self.cluster = None
        self.account = None
        self.partition = None
        self.share = None
        self.max_jobs = None
        self.max_nodes = None
        self.Max_cpus = None
        self.max_submit = None
        self.max_wall = None
        self.max_cpu_mins = None
        self.qos = None
        self.def_qos = None

    def __str__(self):
        return """Slurm User(username: {}, def_account: {}, admin: {}, cluster: {},
        account: {}, partition: {}, share: {}, max_jobs: {}, max_nodes: {},
        Max_cpus: {}, max_submit: {}, max_wall: {}, max_cpu_mins: {}, qos: {},
        def_qos: {}""".format(self.username, self.def_account, self.admin,
                              self.cluster, self.account, self.partition,
                              self.share, self.max_jobs, self.max_nodes,
                              self.Max_cpus, self.max_submit, self.max_wall,
                              self.max_cpu_mins, self.qos, self.def_qos)

"""
This library is for holding SLURM.conf Partition type data
GPL licensing
"""


class PartitionType:
    def __init__(self):
        self.alloc_nodes = None
        self.allow_accounts = None
        self.allow_groups = None
        self.allow_qos = None
        self.alternate = None
        self.cpubind = None
        self.default = None
        self.def_cpu_per_gpu = None
        self.def_mem_per_cpu = None
        self.def_mem_per_gpu = None
        self.def_mem_per_node = None
        self.deny_accounts = None
        self.deny_qos = None
        self.default_time = None
        self.disable_root_jobs = None
        self.exclusive_user = None
        self.grace_time = None
        self.hidden = None
        self.lnn = None
        self.max_cpus_per_node = None
        self.max_mem_per_cpu = None
        self.max_mem_per_node = None
        self.max_Nodes = None
        self.over_subscribe = None
        self.max_time = None
        self.nodes = None
        self.partition_name = None
        self.preempt_mode = None
        self.priority_job_factor = None
        self.priority_tier = None
        self.qos = None
        self.req_resv = None
        self.root_only = None
        self.select_type_parameters = None
        self.state = None
        self.tres_billing_weights = None

    def __str__(self):
        return """partition: {}( alloc_nodes:{}, allow_accounts:{}, allow_groups:{},
        allow_qos:{}, alternate:{}, cpubind:{}, default:{}, def_cpu_per_gpu:{},
        def_mem_per_cpu:{}, def_mem_per_gpu:{}, def_mem_per_node:{},
        deny_accounts:{}, deny_qos:{}, default_time:{}, disable_root_jobs:{},
        exclusive_user:{}, grace_time:{}, hidden:{}, lnn:{},
        max_cpus_per_node:{}, max_mem_per_cpu:{}, max_mem_per_node:{},
        max_Nodes:{}, over_subscribe:{}, max_time:{}, nodes:{},
        preempt_mode:{}, priority_job_factor:{}, priority_tier:{}, qos:{},
        req_resv:{}, root_only:{}, select_type_parameters:{}, state:{},
        tres_billing_weights:{})""".format(
            self.partition_name,
            self.alloc_nodes,
            self.allow_accounts,
            self.allow_groups,
            self.allow_qos,
            self.alternate,
            self.cpubind,
            self.default,
            self.def_cpu_per_gpu,
            self.def_mem_per_cpu,
            self.def_mem_per_gpu,
            self.def_mem_per_node,
            self.deny_accounts,
            self.deny_qos,
            self.default_time,
            self.disable_root_jobs,
            self.exclusive_user,
            self.grace_time,
            self.hidden,
            self.lnn,
            self.max_cpus_per_node,
            self.max_mem_per_cpu,
            self.max_mem_per_node,
            self.max_Nodes,
            self.over_subscribe,
            self.max_time,
            self.nodes,
            self.preempt_mode,
            self.priority_job_factor,
            self.priority_tier,
            self.qos,
            self.req_resv,
            self.root_only,
            self.select_type_parameters,
            self.state,
            self.tres_billing_weights)

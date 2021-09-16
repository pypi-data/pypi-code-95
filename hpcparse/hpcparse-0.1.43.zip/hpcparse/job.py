class Job:
    def __init__(self):
        self.account = None
        self.admin_comment = None
        self.alloc_cpus = None
        self.alloc_gres = None
        self.alloc_nodes = None
        self.alloc_tres = None
        self.assoc_id = None
        self.ave_cpu = None
        self.ave_cpu_freq = None
        self.ave_disk_read = None
        self.ave_disk_write = None
        self.ave_pages = None
        self.ave_rss = None
        self.ave_vm_size = None
        self.block_id = None
        self.cluster = None
        self.comment = None
        self.consumed_energy = None
        self.consumed_energy_raw = None
        self.cpu_time = None
        self.cpu_time_raw = None
        self.derived_exit_code = None
        self.elapsed = None
        self.elapsed_raw = None
        self.eligible = None
        self.end = None
        self.exit_code = None
        self.gid = None
        self.group = None
        self.job_id = None
        self.job_id_raw = None
        self.job_name = None
        self.layout = None
        self.max_disk_read = None
        self.max_disk_read_node = None
        self.max_disk_read_task = None
        self.max_disk_write = None
        self.max_disk_write_node = None
        self.max_disk_write_task = None
        self.max_pages = None
        self.max_pages_node = None
        self.max_pages_task = None
        self.memory = None
        self.memory_node = None
        self.memory_task = None
        self.max_vm_size = None
        self.max_vm_size_node = None
        self.max_vm_size_task = None
        self.mcs_label = None
        self.min_cpu = None
        self.min_cpu_node = None
        self.min_cpu_task = None
        self.num_cpus = None
        self.num_nodes = None
        self.node_list = None
        self.num_tasks = None
        self.priority = None
        self.partition = None
        self.qos = None
        self.qos_raw = None
        self.req_cpu_freq = None
        self.req_cpu_freq_min = None
        self.req_cpu_freq_max = None
        self.req_cpu_freq_gov = None
        self.req_cpuS = None
        self.req_gres = None
        self.req_mem = None
        self.req_nodes = None
        self.req_tres = None
        self.reservation = None
        self.reservation_Id = None
        self.reserved = None
        self.resv_cpu = None
        self.resv_cpu_raw = None
        self.start = None
        self.state = None
        self.submit = None
        self.suspended = None
        self.system_cpu = None
        self.system_comment = None
        self.time_limit = None
        self.time_limit_raw = None
        self.total_cpu = None
        self.tres_usage_in_ave = None
        self.tres_usage_in_max = None
        self.tres_usage_in_max_node = None
        self.tres_usage_in_max_task = None
        self.tres_usage_in_min = None
        self.tres_usage_in_min_node = None
        self.tres_usage_in_min_task = None
        self.tres_usage_in_tot = None
        self.tres_usage_out_ave = None
        self.tres_usage_out_max = None
        self.tres_usage_out_max_node = None
        self.tres_usage_out_max_task = None
        self.tres_usage_out_min = None
        self.tres_usage_out_min_node = None
        self.tres_usage_out_min_task = None
        self.tres_usage_out_tot = None
        self.uid = None
        self.user = None
        self.user_cpu = None
        self.wc_key = None
        self.wc_key_id = None
        self.working_dir = None
        self.granted_pe = None
        self.catagotries = None

    def __str__(self):
        return """Job ( account: {}, admin_comment: {}, alloc_cpus: {},
        alloc_gres: {}, alloc_nodes: {}, alloc_tres: {}, assoc_id: {},
        ave_cpu: {}, ave_cpu_freq: {}, ave_disk_read: {},
        ave_disk_write: {}, ave_pages: {}, ave_rss: {}, ave_vm_size: {},
        block_id: {}, cluster: {}, comment: {}, consumed_energy: {},
        consumed_energy_raw: {}, cpu_time {}, cpu_time_raw: {},
        derived_exit_code: {}, elapsed: {}, elapsed_raw: {},
        end: {}, exit_code: {}, gid: {}, group: {}, job_id: {}, job_id_raw: {},
        job_name: {}, layout: {}, max_disk_read: {}, max_disk_read_node: {},
        max_disk_read_task: {}, max_disk_write: {}, max_disk_write_node: {},
        max_disk_write_task: {}, max_pages: {}, max_pages_node: {},
        max_pages_task: {}, memory: {}, memory_node: {}, memory_task: {},
        max_vm_size: {}, max_vm_size_node: {}, max_vm_size_task: {},
        mcs_label: {}, min_cpu: {}, min_cpu_node: {}, min_cpu_task: {},
        NcpuS: {}, NNodes: {}, node_list: {}, num_tasks: {}, priority: {},
        partition: {}, qos: {}, qos_raw: {}, req_cpu_freq: {},
        req_cpu_freq_min: {}, req_cpu_freq_max: {}, req_cpu_freq_gov: {},
        req_cpuS: {}, req_gres: {}, req_mem: {}, req_nodes: {}, req_tres: {},
        reservation: {}, reservatio_id: {}, reserved: {}, resv_cpu: {},
        resv_cpu_raw: {}, start: {}, state: {}, submit: {}, susspended: {},
        system_cpu: {}, system_comment: {}, time_limit: {}, time_limit_raw: {},
        total_cpu: {}, tres_usage_in_ave: {}, tres_usage_in_max: {},
        tres_usage_in_max_node: {}, tres_usage_in_max_task: {},
        tres_usage_in_min: {}, tres_usage_in_min_node: {},
        tres_usage_in_min_task: {}, tres_usage_in_tot: {},
        tres_usage_out_ave: {}, tres_usage_out_max: {},
        tres_usage_out_max_node: {}, tres_usage_out_max_task: {},
        tres_usage_out_min: {}, tres_usage_out_min_node: {},
        tres_usage_out_min_task: {}, tres_usage_out_tot: {}, uid: {}, user: {},
        user_cpu: {}, wc_key: {}, wc_key_id: {}, working_dir: {},
        granted_pe: {}, catagories: {})""".format(self.account,
                                                  self.admin_comment,
                                                  self.alloc_cpus,
                                                  self.alloc_gres,
                                                  self.alloc_nodes,
                                                  self.alloc_tres,
                                                  self.assoc_id,
                                                  self.ave_cpu,
                                                  self.ave_cpu_freq,
                                                  self.ave_disk_read,
                                                  self.ave_disk_write,
                                                  self.ave_pages,
                                                  self.ave_rss,
                                                  self.ave_vm_size,
                                                  self.block_id,
                                                  self.cluster,
                                                  self.comment,
                                                  self.consumed_energy,
                                                  self.consumed_energy_raw,
                                                  self.cpu_time,
                                                  self.cpu_time_raw,
                                                  self.derived_exit_code,
                                                  self.elapsed,
                                                  self.elapsed_raw,
                                                  self.end,
                                                  self.exit_code,
                                                  self.gid,
                                                  self.group,
                                                  self.job_id,
                                                  self.job_id_raw,
                                                  self.job_name,
                                                  self.layout,
                                                  self.max_disk_read,
                                                  self.max_disk_read_node,
                                                  self.max_disk_read_task,
                                                  self.max_disk_write,
                                                  self.max_disk_write_node,
                                                  self.max_disk_write_task,
                                                  self.max_pages,
                                                  self.max_pages_node,
                                                  self.max_pages_task,
                                                  self.memory,
                                                  self.memory_node,
                                                  self.memory_task,
                                                  self.max_vm_size,
                                                  self.max_vm_size_node,
                                                  self.max_vm_size_task,
                                                  self.mcs_label,
                                                  self.min_cpu,
                                                  self.min_cpu_node,
                                                  self.min_cpu_task,
                                                  self.num_cpus,
                                                  self.num_nodes,
                                                  self.node_list,
                                                  self.num_tasks,
                                                  self.priority,
                                                  self.partition,
                                                  self.qos_raw,
                                                  self.qos_raw,
                                                  self.req_cpu_freq,
                                                  self.req_cpu_freq_min,
                                                  self.req_cpu_freq_max,
                                                  self.req_cpu_freq_gov,
                                                  self.req_cpuS,
                                                  self.req_gres,
                                                  self.req_mem,
                                                  self.req_nodes,
                                                  self.req_tres,
                                                  self.reservation,
                                                  self.reservation_Id,
                                                  self.reserved,
                                                  self.resv_cpu,
                                                  self.resv_cpu_raw,
                                                  self.start,
                                                  self.state,
                                                  self.submit,
                                                  self.suspended,
                                                  self.system_cpu,
                                                  self.system_comment,
                                                  self.time_limit,
                                                  self.time_limit_raw,
                                                  self.total_cpu,
                                                  self.tres_usage_in_ave,
                                                  self.tres_usage_in_max,
                                                  self.tres_usage_in_max_node,
                                                  self.tres_usage_in_max_task,
                                                  self.tres_usage_in_min,
                                                  self.tres_usage_in_min_node,
                                                  self.tres_usage_in_min_task,
                                                  self.tres_usage_in_tot,
                                                  self.tres_usage_out_ave,
                                                  self.tres_usage_out_max,
                                                  self.tres_usage_out_max_node,
                                                  self.tres_usage_out_max_task,
                                                  self.tres_usage_out_min,
                                                  self.tres_usage_out_min_node,
                                                  self.tres_usage_out_min_task,
                                                  self.tres_usage_out_tot,
                                                  self.uid,
                                                  self.user,
                                                  self.user_cpu,
                                                  self.wc_key,
                                                  self.wc_key_id,
                                                  self.working_dir,
                                                  self.granted_pe,
                                                  self.catagotries)

    def __repr__(self):
        return str(self.__dict__)

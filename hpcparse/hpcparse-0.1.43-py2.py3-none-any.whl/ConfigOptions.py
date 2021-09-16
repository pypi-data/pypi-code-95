"""
This library is for holding SLURM.conf configurtion options
"""


class ConfigOptions:
    def __init__(self):
        self.set_accounting_storage_backup_host = None
        self.accounting_storage_enforce = None
        self.accounting_storage_extenal_host = None
        self.accounting_storage_host = None
        self.accounting_storage_loc = None
        self.accounting_storage_pass = None
        self.accounting_storage_port = None
        self.accounting_storage_tres = None
        self.accounting_storage_type = None
        self.accounting_storage_user = None
        self.accounting_store_job_comment = None
        self.acct_gather_node_freq = None
        self.acct_gather_energy_type = None
        self.acct_gather_infiniband_type = None
        self.acct_gather_filesystem_type = None
        self.acct_gather_profile_type = None
        self.allow_spec_resources_usage = None
        self.auth_alt_types = None
        self.auth_type = None
        self.batch_start_timeout = None
        self.burst_buffer_type = None
        self.cli_filter_plugins = None
        self.cluster_name = None
        self.communication_parameters = None
        self.complete_wait = None
        self.cors_spec_plugin = None
        self.cpu_freq_def = None
        self.cpu_freq_governors = None
        self.cred_type = None
        self.debug_flags = None
        self.def_cpu_per_gpu = None
        self.def_mem_per_cpu = None
        self.def_mem_per_gpu = None
        self.def_mem_per_node = None
        self.default_storage_host = None
        self.default_storage_loc = None
        self.default_storage_pass = None
        self.default_storage_port = None
        self.default_storage_type = None
        self.default_storage_user = None
        self.dependency_parameters = None
        self.disable_root_jobs = None
        self.eio_timeout = None
        self.enforce_part_limits = None
        self.epilog = None
        self.epilog_msg_time = None
        self.epilog_slurmctld = None
        self.ext_sensors_freq = None
        self.ext_sensors_type = None
        self.fair_share_dampening_factor = None
        self.federation_parameters = None
        self.first_job_id = None
        self.get_env_timeout = None
        self.gres_types = None
        self.group_update_force = None
        self.group_update_time = None
        self.gpu_update_def = None
        self.health_check_interval = None
        self.health_check_node_state = None
        self.health_check_program = None
        self.inactive_limit = None
        self.job_acct_gather_type = None
        self.job_acct_gather_frequency = None
        self.job_acct_gather_params = None
        self.job_comp_host = None
        self.job_comp_loc = None
        self.job_comp_params = None
        self.job_comp_pass = None
        self.job_comp_port = None
        self.job_comp_type = None
        self.job_comp_user = None
        self.job_container_type = None
        self.job_fie_append = None
        self.job_requeue = None
        self.job_submit_plugins = None
        self.keep_alive_time = None
        self.kill_on_bad_exit = None
        self.kill_wait = None
        self.launch_parameters = None
        self.launch_type = None
        self.license = None
        self.log_time_format = None
        self.mail_domain = None
        self.mail_prog = None
        self.max_array_size = None
        self.max_dbd_msgs = None
        self.max_job_count = None
        self.max_job_id = None
        self.max_mem_per_cpu = None
        self.max_mem_per_node = None
        self.max_step_count = None
        self.max_tasks_per_node = None
        self.mcs_parameters = None
        self.mcs_plugin = None
        self.mem_limit_enforce = None
        self.message_timeout = None
        self.min_job_age = None
        self.mpi_default = None
        self.mpi_params = None
        self.msg_aggregations_params = None
        self.node_features_plugins = None
        self.over_timelimit = None
        self.plugin_dir = None
        self.plug_stack_dir = None
        self.power_parameters = None
        self.power_plugin = None
        self.preempt_mode = None
        self.preempt_type = None
        self.preempt_exempt_time = None
        self.priority_calc_period = None
        self.priority_decay_half_life = None
        self.priority_favor_small = None
        self.priority_flags = None
        self.priority_max_age = None
        self.priority_parameters = None
        self.priority_site_factor_parameters = None
        self.priority_site_factor_plugin = None
        self.priority_type = None
        self.priority_usage_reset_period = None
        self.priority_weight_age = None
        self.priority_weight_assoc = None
        self.priority_weight_fair_share = None
        self.priority_weight_job_size = None
        self.priority_weight_partition = None
        self.priority_weight_qos = None
        self.priority_weight_tres = None
        self.private_data = None
        self.proctrack_type = None
        self.prolog = None
        self.prolog_epilog_timeout = None
        self.prolog_flags = None
        self.prolog_slurmctld = None
        self.propagate_prio_process = None
        self.propagate_resource_limits = None
        self.propagate_resource_limits_except = None
        self.reboot_program = None
        self.reconfig_flags = None
        self.requeue_exit = None
        self.requeue_exit_hold = None
        self.resume_fail_program = None
        self.resume_program = None
        self.resume_rate = None
        self.resume_timeout = None
        self.resv_epilog = None
        self.resv_over_run = None
        self.resv_prolog = None
        self.return_to_service = None
        self.route_pligin = None
        self.salloc_default_command = None
        self.sbcast_parameters = None
        self.scheduler_parameters = None
        self.scheduler_time_slice = None
        self.scheduler_type = None
        self.select_type = None
        self.select_type_parameters = None
        self.slurm_user = None
        self.slurmctld_addr = None
        self.slurmctld_debug = None
        self.slurmctld_host = None
        self.slurmctld_log_file = None
        self.slurmctld_parameters = None
        self.slurmctld_pid_file = None
        self.slurmctld_plug_stack = None
        self.slurmctld_port = None
        self.slurmctld_primary_off_prog = None
        self.slurmctld_primary_on_prog = None
        self.slurmctld_syslog_debug = None
        self.slurmctld_timeout = None
        self.slurmd_debug = None
        self.slurmd_log_file = None
        self.slurmd_parameters = None
        self.slurmd_pid_file = None
        self.slurmd_port = None
        self.slurmd_spool_dir = None
        self.slurmd_syslog_debug = None
        self.slurmd_timeout = None
        self.slurmd_user = None
        self.slurm_sched_log_file = None
        self.slurm_sched_log_level = None
        self.srun_epilog = None
        self.srun_port_range = None
        self.srun_prolog = None
        self.state_save_location = None
        self.suspend_exc_nodes = None
        self.suspend_exc_parts = None
        self.suspend_program = None
        self.suspend_rate = None
        self.suspend_time = None
        self.suspend_timeout = None
        self.switch_type = None
        self.task_epilog = None
        self.task_plugin = None
        self.task_plugin_param = None
        self.task_prolog = None
        self.tcp_timeout = None
        self.tmp_fs = None
        self.topology_param = None
        self.topology_plugin = None
        self.track_wc_key = None
        self.tree_width = None
        self.unkillable_step_program = None
        self.unkillable_step_timeout = None
        self.use_pam = None
        self.v_size_factor = None
        self.wait_time = None
        self.x11_parameters = None

    # Function for defining out put string for Configuration optins
    def __str__(self):
        return """configuration Options (set_accounting_storage_backup_host:{},
        accounting_storage_enforce:{}, accounting_storage_extenal_host:{},
        accounting_storage_host:{}, accounting_storage_loc:{},
        accounting_storage_pass:{}, accounting_storage_port:{},
        accounting_storage_tres:{}, accounting_storage_type:{},
        accounting_storage_user:{}, accounting_store_job_comment:{},
        acct_gather_node_freq:{}, acct_gather_energy_type:{},
        acct_gather_infiniband_type:{}, acct_gather_filesystem_type:{},
        acct_gather_profile_type:{}, allow_spec_resources_usage:{},
        auth_alt_types:{}, auth_type:{}, batch_start_timeout:{},
        burst_buffer_type:{}, cli_filter_plugins:{}, cluster_name:{},
        communication_parameters:{}, complete_wait:{}, cors_spec_plugin:{},
        cpu_freq_def:{}, cpu_freq_governors:{}, cred_type:{}, debug_flags:{},
        def_cpu_per_gpu:{}, def_mem_per_cpu:{}, def_mem_per_gpu:{},
        def_mem_per_node:{}, default_storage_host:{}, default_storage_loc:{},
        default_storage_pass:{}, default_storage_port:{},
        default_storage_type:{}, default_storage_user:{},
        dependency_parameters:{}, disable_root_jobs:{}, eio_timeout:{},
        enforce_part_limits:{}, epilog:{}, epilog_msg_time:{},
        epilog_slurmctld:{}, ext_sensors_freq:{}, ext_sensors_type:{},
        fair_share_dampening_factor:{}, federation_parameters:{},
        first_job_id:{}, get_env_timeout:{}, gres_types:{},
        group_update_force:{}, group_update_time:{}, gpu_update_def:{},
        health_check_interval:{}, health_check_node_state:{},
        health_check_program:{}, inactive_limit:{}, job_acct_gather_type:{},
        job_acct_gather_frequency:{}, job_acct_gather_params:{},
        job_comp_host:{}, job_comp_loc:{}, job_comp_params:{},
        job_comp_pass:{}, job_comp_port:{}, job_comp_type:{}, job_comp_user:{},
        job_container_type:{}, job_fie_append:{}, job_requeue:{},
        job_submit_plugins:{}, keep_alive_time:{}, kill_on_bad_exit:{},
        kill_wait:{}, launch_parameters:{}, launch_type:{}, license:{},
        log_time_format:{}, mail_domain:{}, mail_prog:{}, max_array_size:{},
        max_dbd_msgs:{}, max_job_count:{}, max_job_id:{}, max_mem_per_cpu:{},
        max_mem_per_node:{}, max_step_count:{}, max_tasks_per_node:{},
        mcs_parameters:{}, mcs_plugin:{}, mem_limit_enforce:{},
        message_timeout:{}, min_job_age:{}, mpi_default:{}, mpi_params:{},
        msg_aggregations_params:{}, node_features_plugins:{},
        over_timelimit:{}, plugin_dir:{}, plug_stack_dir:{},
        power_parameters:{}, power_plugin:{}, preempt_mode:{},
        preempt_type:{}, preempt_exempt_time:{}, priority_calc_period:{},
        priority_decay_half_life:{}, priority_favor_small:{},
        priority_flags:{}, priority_max_age:{}, priority_parameters:{},
        priority_site_factor_parameters:{}, priority_site_factor_plugin:{},
        priority_type:{}, priority_usage_reset_period:{},
        priority_weight_age:{}, priority_weight_assoc:{},
        priority_weight_fair_share:{}, priority_weight_job_size:{},
        priority_weight_partition:{}, priority_weight_qos:{},
        priority_weight_tres:{}, private_data:{}, proctrack_type:{}, prolog:{},
        prolog_epilog_timeout:{}, prolog_flags:{}, prolog_slurmctld:{},
        propagate_prio_process:{}, propagate_resource_limits:{},
        propagate_resource_limits_except:{}, reboot_program:{},
        reconfig_flags:{}, requeue_exit:{}, requeue_exit_hold:{},
        resume_fail_program:{}, resume_program:{}, resume_rate:{},
        resume_timeout:{}, resv_epilog:{}, resv_over_run:{}, resv_prolog:{},
        return_to_service:{}, route_pligin:{}, salloc_default_command:{},
        sbcast_parameters:{}, scheduler_parameters:{}, scheduler_time_slice:{},
        scheduler_type:{}, select_type:{}, select_type_parameters:{},
        slurm_user:{}, slurmctld_addr:{}, slurmctld_debug:{},
        slurmctld_host:{}, slurmctld_log_file:{}, slurmctld_parameters:{},
        slurmctld_pid_file:{}, slurmctld_plug_stack:{}, slurmctld_port:{},
        slurmctld_primary_off_prog:{}, slurmctld_primary_on_prog:{},
        slurmctld_syslog_debug:{}, slurmctld_timeout:{}, slurmd_debug:{},
        slurmd_log_file:{}, slurmd_parameters:{}, slurmd_pid_file:{},
        slurmd_port:{}, slurmd_spool_dir:{}, slurmd_syslog_debug:{},
        slurmd_timeout:{}, slurmd_user:{}, slurm_sched_log_file:{},
        slurm_sched_log_level:{}, srun_epilog:{}, srun_port_range:{},
        srun_prolog:{}, state_save_location:{}, suspend_exc_nodes:{},
        suspend_exc_parts:{}, suspend_program:{}, suspend_rate:{},
        suspend_time:{}, suspend_timeout:{}, switch_type:{}, task_epilog:{},
        task_plugin:{}, task_plugin_param:{}, task_prolog:{}, tcp_timeout:{},
        tmp_fs:{}, topology_param:{}, topology_plugin:{}, track_wc_key:{},
        tree_width:{}, unkillable_step_program:{}, unkillable_step_timeout:{},
        use_pam:{}, v_size_factor:{}, wait_time:{},
        x11_parameters:{}, """.format(self.set_accounting_storage_backup_host,
                                      self.accounting_storage_enforce,
                                      self.accounting_storage_extenal_host,
                                      self.accounting_storage_host,
                                      self.accounting_storage_loc,
                                      self.accounting_storage_pass,
                                      self.accounting_storage_port,
                                      self.accounting_storage_tres,
                                      self.accounting_storage_type,
                                      self.accounting_storage_user,
                                      self.accounting_store_job_comment,
                                      self.acct_gather_node_freq,
                                      self.acct_gather_energy_type,
                                      self.acct_gather_infiniband_type,
                                      self.acct_gather_filesystem_type,
                                      self.acct_gather_profile_type,
                                      self.allow_spec_resources_usage,
                                      self.auth_alt_types,
                                      self.auth_type,
                                      self.batch_start_timeout,
                                      self.burst_buffer_type,
                                      self.cli_filter_plugins,
                                      self.cluster_name,
                                      self.communication_parameters,
                                      self.complete_wait,
                                      self.cors_spec_plugin,
                                      self.cpu_freq_def,
                                      self.cpu_freq_governors,
                                      self.cred_type,
                                      self.debug_flags,
                                      self.def_cpu_per_gpu,
                                      self.def_mem_per_cpu,
                                      self.def_mem_per_gpu,
                                      self.def_mem_per_node,
                                      self.default_storage_host,
                                      self.default_storage_loc,
                                      self.default_storage_pass,
                                      self.default_storage_port,
                                      self.default_storage_type,
                                      self.default_storage_user,
                                      self.dependency_parameters,
                                      self.disable_root_jobs,
                                      self.eio_timeout,
                                      self.enforce_part_limits,
                                      self.epilog,
                                      self.epilog_msg_time,
                                      self.epilog_slurmctld,
                                      self.ext_sensors_freq,
                                      self.ext_sensors_type,
                                      self.fair_share_dampening_factor,
                                      self.federation_parameters,
                                      self.first_job_id,
                                      self.get_env_timeout,
                                      self.gres_types,
                                      self.group_update_force,
                                      self.group_update_time,
                                      self.gpu_update_def,
                                      self.health_check_interval,
                                      self.health_check_node_state,
                                      self.health_check_program,
                                      self.inactive_limit,
                                      self.job_acct_gather_type,
                                      self.job_acct_gather_frequency,
                                      self.job_acct_gather_params,
                                      self.job_comp_host,
                                      self.job_comp_loc,
                                      self.job_comp_params,
                                      self.job_comp_pass,
                                      self.job_comp_port,
                                      self.job_comp_type,
                                      self.job_comp_user,
                                      self.job_container_type,
                                      self.job_fie_append,
                                      self.job_requeue,
                                      self.job_submit_plugins,
                                      self.keep_alive_time,
                                      self.kill_on_bad_exit,
                                      self.kill_wait,
                                      self.launch_parameters,
                                      self.launch_type,
                                      self.license,
                                      self.log_time_format,
                                      self.mail_domain,
                                      self.mail_prog,
                                      self.max_array_size,
                                      self.max_dbd_msgs,
                                      self.max_job_count,
                                      self.max_job_id,
                                      self.max_mem_per_cpu,
                                      self.max_mem_per_node,
                                      self.max_step_count,
                                      self.max_tasks_per_node,
                                      self.mcs_parameters,
                                      self.mcs_plugin,
                                      self.mem_limit_enforce,
                                      self.message_timeout,
                                      self.min_job_age,
                                      self.mpi_default,
                                      self.mpi_params,
                                      self.msg_aggregations_params,
                                      self.node_features_plugins,
                                      self.over_timelimit,
                                      self.plugin_dir,
                                      self.plug_stack_dir,
                                      self.power_parameters,
                                      self.power_plugin,
                                      self.preempt_mode,
                                      self.preempt_type,
                                      self.preempt_exempt_time,
                                      self.priority_calc_period,
                                      self.priority_decay_half_life,
                                      self.priority_favor_small,
                                      self.priority_flags,
                                      self.priority_max_age,
                                      self.priority_parameters,
                                      self.priority_site_factor_parameters,
                                      self.priority_site_factor_plugin,
                                      self.priority_type,
                                      self.priority_usage_reset_period,
                                      self.priority_weight_age,
                                      self.priority_weight_assoc,
                                      self.priority_weight_fair_share,
                                      self.priority_weight_job_size,
                                      self.priority_weight_partition,
                                      self.priority_weight_qos,
                                      self.priority_weight_tres,
                                      self.private_data,
                                      self.proctrack_type,
                                      self.prolog,
                                      self.prolog_epilog_timeout,
                                      self.prolog_flags,
                                      self.prolog_slurmctld,
                                      self.propagate_prio_process,
                                      self.propagate_resource_limits,
                                      self.propagate_resource_limits_except,
                                      self.reboot_program,
                                      self.reconfig_flags,
                                      self.requeue_exit,
                                      self.requeue_exit_hold,
                                      self.resume_fail_program,
                                      self.resume_program,
                                      self.resume_rate,
                                      self.resume_timeout,
                                      self.resv_epilog,
                                      self.resv_over_run,
                                      self.resv_prolog,
                                      self.return_to_service,
                                      self.route_pligin,
                                      self.salloc_default_command,
                                      self.sbcast_parameters,
                                      self.scheduler_parameters,
                                      self.scheduler_time_slice,
                                      self.scheduler_type,
                                      self.select_type,
                                      self.select_type_parameters,
                                      self.slurm_user,
                                      self.slurmctld_addr,
                                      self.slurmctld_debug,
                                      self.slurmctld_host,
                                      self.slurmctld_log_file,
                                      self.slurmctld_parameters,
                                      self.slurmctld_pid_file,
                                      self.slurmctld_plug_stack,
                                      self.slurmctld_port,
                                      self.slurmctld_primary_off_prog,
                                      self.slurmctld_primary_on_prog,
                                      self.slurmctld_syslog_debug,
                                      self.slurmctld_timeout,
                                      self.slurmd_debug,
                                      self.slurmd_log_file,
                                      self.slurmd_parameters,
                                      self.slurmd_pid_file,
                                      self.slurmd_port,
                                      self.slurmd_spool_dir,
                                      self.slurmd_syslog_debug,
                                      self.slurmd_timeout,
                                      self.slurmd_user,
                                      self.slurm_sched_log_file,
                                      self.slurm_sched_log_level,
                                      self.srun_epilog,
                                      self.srun_port_range,
                                      self.srun_prolog,
                                      self.state_save_location,
                                      self.suspend_exc_nodes,
                                      self.suspend_exc_parts,
                                      self.suspend_program,
                                      self.suspend_rate,
                                      self.suspend_time,
                                      self.suspend_timeout,
                                      self.switch_type,
                                      self.task_epilog,
                                      self.task_plugin,
                                      self.task_plugin_param,
                                      self.task_prolog,
                                      self.tcp_timeout,
                                      self.tmp_fs,
                                      self.topology_param,
                                      self.topology_plugin,
                                      self.track_wc_key,
                                      self.tree_width,
                                      self.unkillable_step_program,
                                      self.unkillable_step_timeout,
                                      self.use_pam,
                                      self.v_size_factor,
                                      self.wait_time,
                                      self.x11_parameters)

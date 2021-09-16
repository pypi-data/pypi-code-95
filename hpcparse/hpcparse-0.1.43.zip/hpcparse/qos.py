class QOS():
    def __init__(self):
        self.name = None
        self.priority = None
        self.grace_time = None
        self.preempt = None
        self.preempt_mode = None
        self.flags = None
        self.usage_thres = None
        self.usage_factor = None
        self.group_tres = None
        self.group_tres_mins = None
        self.group_tres_run_mins = None
        self.group_jobs = None
        self.group_submit = None
        self.group_wall = None
        self.max_tres = None
        self.max_tres_per_node = None
        self.max_tres_mins = None
        self.max_wall = None
        self.max_tres_pu = None
        self.max_jobs_pu = None
        self.max_submit_pu = None
        self.max_tres_pa = None
        self.max_jobs_pa = None
        self.max_submit_pa = None
        self.min_tres = None

    def __str__(self):
        return """QOS Parameters (Name: {}, Priority: {}, Grace Time: {}, Preempt: {},
        Preempt Mode: {}, Flags: {}, Usage Thres: {}, Usage Factor: {},
        Group TRES: {}, Group TRES Mins: {}, Group TRES Run Mins: {},
        Group Jobs: {}, Group Submit: {}, Group Wall: {}, Max TRES: {},
        Max TRES Per Node: {}, Max TRES Mins: {}, Max Wall: {},
        Max TRES PU: {}, Max Jobs PU: {}, Max Submit PU: {}, Max TRES PA: {},
        Max Jobs PA: {}, Max Submit PA: {}, Min TRES: {}"""\
            .format(self.name, self.priority, self.grace_time, self.preempt,
                    self.preempt_mode, self.flags, self.usage_thres,
                    self.usage_factor, self.group_tres, self.group_tres_mins,
                    self.group_tres_run_mins, self.group_jobs,
                    self.group_submit, self.group_wall, self.max_tres,
                    self.max_tres_per_node, self.max_tres_mins, self.max_wall,
                    self.max_tres_pu, self.max_jobs_pu, self.max_submit_pu,
                    self.max_tres_pa, self.max_jobs_pa, self.max_submit_pa,
                    self.min_tres)

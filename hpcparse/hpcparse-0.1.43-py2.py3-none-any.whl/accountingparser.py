# Libs
import csv
from collections import defaultdict

# Own Modules
from hpcparse.job import Job


# Accounting Parser Class Definition
class AccountingParser:

    # Method for Parsing SGE Accounting Files
    @classmethod
    def sge_parser(cls, filepath, num_lines=0, start=0):
        """
        sge_parser()
        Parse SGE accounting files and return a list of jobs.
        """
        # initialize joblist
        joblist = []
        count = 0
        # Setting the Colum Headers for SGE csv as they are not included in
        # the header
        dictValues = ['qname', 'hostname', 'group', 'owner', 'job_name',
                      'job_id', 'account', 'priority', 'submission_time',
                      'start_time', 'end_time', 'failed', 'exit_status',
                      'ru_wallclock', 'ru_utime', 'ru_stime', 'ru_maxrss',
                      'ru_ixrss', 'ruismrss', 'ru_idrss', 'ru_isrss',
                      'ruminflt', 'ru_majflt', 'ru_nswap', 'ru_inblock',
                      'ru_outblock', 'ru_msgsnd', 'ru_msgrcv', 'ru_nsignals',
                      'ru_nvcsw', 'ru_nivcsw', 'project', 'department',
                      'granted_pe', 'slots', 'task_number', 'cpu', 'mem', 'io',
                      'catagory', 'iow', 'pe_taskid', 'maxvmem', 'arid',
                      'ar_submission_time']

        # Reading in the csv file and creating job objects
        try:
            with open(filepath, 'r', newline='') as inputFile:
                records = csv.DictReader(inputFile, fieldnames=dictValues,
                                         delimiter=':')
                for row in records:
                    # Use default dict to put None in where items are missing
                    row = defaultdict(lambda: None, row)
                    try:
                        # Break if we have reached the number of lines to read.
                        if num_lines > 0 and\
                           count == num_lines:
                            break

                        if start >= 0 and count < start:
                            start -= 1
                            continue

                        count += 1
                        # Initialize new job object
                        new_job = Job()
                        # Need to adjust for SGE parameters. Not all are done
                        new_job.account = row['Account']
                        new_job.admin_comment = row['AdminComment']
                        new_job.alloc_cpus = row['AllocCPUS']
                        new_job.alloc_gres = row['AllocGRES']
                        new_job.alloc_nodes = row['AllocNodes']
                        new_job.alloc_tres = row['AllocTRES']
                        new_job.assoc_id = row['AssocID']
                        new_job.ave_cpu = row['AveCPU']
                        new_job.ave_cpu_freq = row['AveCPUFreq']
                        new_job.ave_disk_read = row['AveDiskRead']
                        new_job.ave_disk_write = row['AveDiskWrite']
                        new_job.ave_pages = row['AvePages']
                        new_job.ave_rss = row['AveRSS']
                        new_job.ave_vm_size = row['AveVMSize']
                        new_job.block_ID = row['BlockID']
                        new_job.cluster = row['Cluster']
                        new_job.comment = row['Comment']
                        new_job.consumed_energy = row['ConsumedEnergy']
                        new_job.consumed_energy_raw = row['ConsumedEnergyRaw']
                        new_job.cpu_time = row['CPUTime']
                        new_job.cpu_time_raw = row['cpu']
                        new_job.derived_exit_code = row['exit_status']
                        new_job.elapsed = row['ru_wallclock']
                        new_job.elapsed_raw = row['ElapsedRaw']
                        new_job.eligible = row['Eligible']
                        new_job.end = row['End']
                        new_job.exit_code = row['ExitCode']
                        new_job.gid = row['GID']
                        new_job.group = row['Group']
                        new_job.job_id = row['JobID']
                        new_job.job_id_raw = row['JobIDRaw']
                        new_job.job_name = row['JobName']
                        new_job.layout = row['Layout']
                        new_job.max_disk_read = row['MaxDiskRead']
                        new_job.max_disk_read_node = row['MaxDiskReadNode']
                        new_job.max_disk_read_task = row['MaxDiskReadTask']
                        new_job.max_disk_write = row['MaxDiskWrite']
                        new_job.max_disk_write_node = row['MaxDiskWriteNode']
                        new_job.max_disk_write_task = row['MaxDiskWriteTask']
                        new_job.max_pages = row['MaxPages']
                        new_job.max_pages_node = row['MaxPagesNode']
                        new_job.max_pages_task = row['MaxPagesTask']
                        new_job.memory = row['MaxRSS']
                        new_job.memory_node = row['MaxRSSNode']
                        new_job.memory_task = row['MaxRSSTask']
                        new_job.max_vm_size = row['MaxVMSize']
                        new_job.max_vm_size_node = row['MaxVMSizeNode']
                        new_job.max_vm_size_task = row['MaxVMSizeTask']
                        new_job.mcs_label = row['McsLabel']
                        new_job.min_cpu = row['MinCPU']
                        new_job.min_cpu_node = row['MinCPUNode']
                        new_job.min_cpu_task = row['MinCPUTask']
                        new_job.num_cpus = row['NCPUS']
                        new_job.num_nodes = row['NNodes']
                        new_job.node_list = row['NodeList']
                        new_job.num_tasks = row['NTasks']
                        new_job.priority = row['Priority']
                        new_job.partition = row['Partition']
                        new_job.qos = row['QOS']
                        new_job.qos_raw = row['QOSRAW']
                        new_job.req_cpu_freq = row['ReqCPUFreq']
                        new_job.req_cpu_freq_min = row['ReqCPUFreqMin']
                        new_job.req_cpu_freq_max = row['ReqCPUFreqMax']
                        new_job.req_cpu_freq_gov = row['ReqCPUFreqGov']
                        new_job.req_cpuS = row['ReqCPUS']
                        new_job.req_gres = row['ReqGRES']
                        new_job.req_mem = row['ReqMem']
                        new_job.req_nodes = row['ReqNodes']
                        new_job.req_tres = row['ReqTRES']
                        new_job.reservation = row['Reservation']
                        new_job.reservation_Id = row['ReservationId']
                        new_job.reserved = row['Reserved']
                        new_job.resv_cpu = row['ResvCPU']
                        new_job.resv_cpu_raw = row['ResvCPURAW']
                        new_job.start = row['start_time']
                        new_job.state = row['State']
                        new_job.submit = row['submission_time']
                        new_job.suspended = row['Suspended']
                        new_job.system_cpu = row['SystemCPU']
                        new_job.system_comment = row['SystemComment']
                        new_job.time_limit = row['Timelimit']
                        new_job.time_limit_raw = row['TimelimitRaw']
                        new_job.total_cpu = row['TotalCPU']
                        new_job.tres_usage_in_ave = row['TRESUsageInAve']
                        new_job.tres_usage_in_max = row['TRESUsageInMax']
                        new_job.tres_usage_in_max_node = \
                            row['TRESUsageInMaxNode']
                        new_job.tres_usage_in_max_task = \
                            row['TRESUsageInMaxTask']
                        new_job.tres_usage_in_min = row['TRESUsageInMin']
                        new_job.tres_usage_in_min_node = \
                            row['TRESUsageInMinNode']
                        new_job.tres_usage_in_min_task = \
                            row['TRESUsageInMinTask']
                        new_job.tres_usage_in_tot = row['TRESUsageInTot']
                        new_job.tres_usage_out_ave = row['TRESUsageOutAve']
                        new_job.tres_usage_out_max = row['TRESUsageOutMax']
                        new_job.tres_usage_out_max_node = \
                            row['TRESUsageOutMaxNode']
                        new_job.tres_usage_out_max_task = \
                            row['TRESUsageOutMaxTask']
                        new_job.tres_usage_out_min = row['TRESUsageOutMin']
                        new_job.tres_usage_out_min_node = \
                            row['TRESUsageOutMinNode']
                        new_job.tres_usage_out_min_task = \
                            row['TRESUsageOutMinTask']
                        new_job.tres_usage_out_tot = row['TRESUsageOutTot']
                        new_job.uid = row['UID']
                        new_job.user = row['owner']
                        new_job.user_cpu = row['UserCPU']
                        new_job.wc_key = row['WCKey']
                        new_job.wc_key_id = row['WCKeyID']
                        new_job.working_dir = row['WorkDir']
                        new_job.granted_pe = row['granted_pe']
                        new_job.catagotries = row['catagories']

                        joblist.append(new_job)
                    except Exception as ex:
                        print(ex)
                        print('There was a parsing error on line: ' + str(
                               count) + '\n\r skipping line and \
                               continuing:')
        except Exception as ex:
            print('error opening File path:' + str(filepath) + ', please check\
                filename and file path: the Exact error \
                follows this message: \n\r')
            print(ex)
            return
        return joblist

    # Method for parsing SLURM accounting files
    @classmethod
    def slurm_parser(cls, filepath, num_lines=0, start=0):

        # Initializing joblist
        joblist = []
        count = 0
        # Reading in SLURM csv accounting file
        try:
            with open(filepath, 'r', newline='') as inputFile:
                records = csv.DictReader(inputFile, delimiter='|')
                for row in records:
                    row = defaultdict(lambda: None, row)
                    try:
                        if num_lines > 0 and \
                           count == num_lines:
                            break

                        if start >= 0 and count < start:
                            start -= 1
                            continue

                        count += 1
                        new_job = Job()
                        new_job.account = row['Account']
                        new_job.admin_comment = row['AdminComment']
                        new_job.alloc_cpus = row['AllocCPUS']
                        new_job.alloc_gres = row['AllocGRES']
                        new_job.alloc_nodes = row['AllocNodes']
                        new_job.alloc_tres = row['AllocTRES']
                        new_job.assoc_id = row['AssocID']
                        new_job.ave_cpu = row['AveCPU']
                        new_job.ave_cpu_freq = row['AveCPUFreq']
                        new_job.ave_disk_read = row['AveDiskRead']
                        new_job.ave_disk_write = row['AveDiskWrite']
                        new_job.ave_pages = row['AvePages']
                        new_job.ave_rss = row['AveRSS']
                        new_job.ave_vm_size = row['AveVMSize']
                        new_job.block_ID = row['BlockID']
                        new_job.cluster = row['Cluster']
                        new_job.comment = row['Comment']
                        new_job.consumed_energy = row['ConsumedEnergy']
                        new_job.consumed_energy_raw = row['ConsumedEnergyRaw']
                        new_job.cpu_time = row['CPUTime']
                        new_job.cpu_time_raw = row['CPUTimeRaw']
                        new_job.derived_exit_code = row['DerivedExitCode']
                        new_job.elapsed = row['Elapsed']
                        new_job.elapsed_raw = row['ElapsedRaw']
                        new_job.eligible = row['Eligible']
                        new_job.end = row['End']
                        new_job.exit_code = row['ExitCode']
                        new_job.gid = row['GID']
                        new_job.group = row['Group']
                        new_job.job_id = row['JobID']
                        new_job.job_id_raw = row['JobIDRaw']
                        new_job.job_name = row['JobName']
                        new_job.layout = row['Layout']
                        new_job.max_disk_read = row['MaxDiskRead']
                        new_job.max_disk_read_node = row['MaxDiskReadNode']
                        new_job.max_disk_read_task = row['MaxDiskReadTask']
                        new_job.max_disk_write = row['MaxDiskWrite']
                        new_job.max_disk_write_node = row['MaxDiskWriteNode']
                        new_job.max_disk_write_task = row['MaxDiskWriteTask']
                        new_job.max_pages = row['MaxPages']
                        new_job.max_pages_node = row['MaxPagesNode']
                        new_job.max_pages_task = row['MaxPagesTask']
                        new_job.memory = row['MaxRSS']
                        new_job.memory_node = row['MaxRSSNode']
                        new_job.memory_task = row['MaxRSSTask']
                        new_job.max_vm_size = row['MaxVMSize']
                        new_job.max_vm_size_node = row['MaxVMSizeNode']
                        new_job.max_vm_size_task = row['MaxVMSizeTask']
                        new_job.mcs_label = row['McsLabel']
                        new_job.min_cpu = row['MinCPU']
                        new_job.min_cpu_node = row['MinCPUNode']
                        new_job.min_cpu_task = row['MinCPUTask']
                        new_job.num_cpus = row['NCPUS']
                        new_job.num_nodes = row['NNodes']
                        new_job.node_list = row['NodeList']
                        new_job.num_tasks = row['NTasks']
                        new_job.priority = row['Priority']
                        new_job.partition = row['Partition']
                        new_job.qos = row['QOS']
                        new_job.qos_raw = row['QOSRAW']
                        new_job.req_cpu_freq = row['ReqCPUFreq']
                        new_job.req_cpu_freq_min = row['ReqCPUFreqMin']
                        new_job.req_cpu_freq_max = row['ReqCPUFreqMax']
                        new_job.req_cpu_freq_gov = row['ReqCPUFreqGov']
                        new_job.req_cpuS = row['ReqCPUS']
                        new_job.req_gres = row['ReqGRES']
                        new_job.req_mem = row['ReqMem']
                        new_job.req_nodes = row['ReqNodes']
                        new_job.req_tres = row['ReqTRES']
                        new_job.reservation = row['Reservation']
                        new_job.reservation_Id = row['ReservationId']
                        new_job.reserved = row['Reserved']
                        new_job.resv_cpu = row['ResvCPU']
                        new_job.resv_cpu_raw = row['ResvCPURAW']
                        new_job.start = row['Start']
                        new_job.state = row['State']
                        # Replace the T that get put in during read in with a
                        # space that should be there
                        new_job.submit = row['Submit'].replace('T', ' ')
                        new_job.suspended = row['Suspended']
                        new_job.system_cpu = row['SystemCPU']
                        new_job.system_comment = row['SystemComment']
                        new_job.time_limit = row['Timelimit']
                        new_job.time_limit_raw = row['TimelimitRaw']
                        new_job.total_cpu = row['TotalCPU']
                        new_job.tres_usage_in_ave = row['TRESUsageInAve']
                        new_job.tres_usage_in_max = row['TRESUsageInMax']
                        new_job.tres_usage_in_max_node = \
                            row['TRESUsageInMaxNode']
                        new_job.tres_usage_in_max_task = \
                            row['TRESUsageInMaxTask']
                        new_job.tres_usage_in_min = row['TRESUsageInMin']
                        new_job.tres_usage_in_min_node = \
                            row['TRESUsageInMinNode']
                        new_job.tres_usage_in_min_task = \
                            row['TRESUsageInMinTask']
                        new_job.tres_usage_in_tot = row['TRESUsageInTot']
                        new_job.tres_usage_out_ave = row['TRESUsageOutAve']
                        new_job.tres_usage_out_max = row['TRESUsageOutMax']
                        new_job.tres_usage_out_max_node = \
                            row['TRESUsageOutMaxNode']
                        new_job.tres_usage_out_max_task = \
                            row['TRESUsageOutMaxTask']
                        new_job.tres_usage_out_min = row['TRESUsageOutMin']
                        new_job.tres_usage_out_min_node = \
                            row['TRESUsageOutMinNode']
                        new_job.tres_usage_out_min_task = \
                            row['TRESUsageOutMinTask']
                        new_job.tres_usage_out_tot = row['TRESUsageOutTot']
                        new_job.uid = row['UID']
                        new_job.user = row['User']
                        new_job.user_cpu = row['UserCPU']
                        new_job.wc_key = row['WCKey']
                        new_job.wc_key_id = row['WCKeyID']
                        new_job.working_dir = row['WorkDir']
                        new_job.granted_pe = row['granted_pe']
                        new_job.catagotries = row['catagories']

                        joblist.append(new_job)
                    except Exception as ex:
                        print('There was a parsing error on line: ' +
                              str(count) + '\n skipping line and \
                              continuing. the Exact error follows this \
                              message: \n')
                        print(ex)
                        return
        except Exception as ex:
            print("error opening File path: {},  please check filename and \
                file path: the Exact error follows this message: "
                  .format(str(filepath)))
            print(ex)
            return
        return joblist

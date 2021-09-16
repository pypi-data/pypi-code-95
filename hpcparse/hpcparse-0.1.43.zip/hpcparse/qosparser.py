# Libs
import csv
from collections import defaultdict

# Own modules
from hpcparse.qos import QOS


class QOSParser:

    @classmethod
    def parse_qos(cls, filepath):
        qos_list = []
        try:
            with open(filepath, 'r', newline='') as inputFile:
                records = csv.DictReader(inputFile, delimiter='|')
                for row in records:
                    row = defaultdict(lambda: None, row)
                    try:
                        new_qos = QOS()

                        new_qos.name = row['Name']
                        new_qos.priority = row['Priority']
                        new_qos.grace_time = row['GraceTime']
                        new_qos.preempt = row['Preempt']
                        new_qos.preempt_mode = row['PreemptMode']
                        new_qos.flags = row['Flags']
                        new_qos.usage_thres = row['UsageThres']
                        new_qos.usage_factor = row['UsageFactor']
                        new_qos.group_tres = row['GrpTRES']
                        new_qos.group_tres_mins = row['GrpTRESMins']
                        new_qos.group_tres_run_mins = row['GrpTRESRunMins']
                        new_qos.group_jobs = row['GrpJobs']
                        new_qos.group_submit = row['GrpSubmit']
                        new_qos.group_wall = row['GrpWall']
                        new_qos.max_tres = row['MaxTRES']
                        new_qos.max_tres_per_node = row['MaxTRESPerNode']
                        new_qos.max_tres_mins = row['MaxTRESMins']
                        new_qos.max_wall = row['MaxWall']
                        new_qos.max_tres_pu = row['MaxTRESPU']
                        new_qos.max_jobs_pu = row['MaxJobsPU']
                        new_qos.max_submit_pu = row['MaxSubmitPU']
                        new_qos.max_tres_pa = row['MaxTRESPA']
                        new_qos.max_jobs_pa = row['MaxJobsPA']
                        new_qos.max_submit_pa = row['MaxSubmitPA']
                        new_qos.min_tres = row['MinTRES']
                        qos_list.append(new_qos)
                    except Exception as ex:
                        print(ex)
                        print('error')
        except Exception as ex:
            print(ex)
            print('error')
        return qos_list

#!/bin/env/python

import datetime
from autosubmitAPIwu.job.job import Job

_COMPLETED_RETRIAL = 1
_FAILED_RETRIAL = 0


def timedelta2hours(deltatime):
    return deltatime.days * 24 + deltatime.seconds / 3600.0


class JobStat(object):
    def __init__(self, name, processors, wallclock):
        self._name = name
        self._processors = processors
        self._wallclock = wallclock
        self.completed_queue_time = datetime.timedelta()
        self.completed_run_time = datetime.timedelta()
        self.failed_queue_time = datetime.timedelta()
        self.failed_run_time = datetime.timedelta()
        self.retrial_count = 0
        self.completed_retrial_count = 0
        self.failed_retrial_count = 0

    def inc_retrial_count(self):
        self.retrial_count += 1

    def inc_completed_retrial_count(self):
        self.completed_retrial_count += 1

    def inc_failed_retrial_count(self):
        self.failed_retrial_count += 1

    @property
    def cpu_consumption(self):
        return timedelta2hours(self._processors * self.completed_run_time) + timedelta2hours(self._processors * self.failed_run_time)

    @property
    def failed_cpu_consumption(self):
        return timedelta2hours(self._processors * self.failed_run_time)

    @property
    def real_consumption(self):
        return timedelta2hours(self.failed_run_time + self.completed_run_time)

    @property
    def expected_real_consumption(self):
        return self._wallclock

    @property
    def expected_cpu_consumption(self):
        return self._wallclock * self._processors

    def get_as_dict(self):
        return {
            "name": self._name,
            "processors": self._processors,
            "wallclock": self._wallclock,
            "completedQueueTime": timedelta2hours(self.completed_queue_time),
            "completedRunTime": timedelta2hours(self.completed_run_time),
            "failedQueueTime": timedelta2hours(self.failed_queue_time),
            "failedRunTime": timedelta2hours(self.failed_run_time),
            "cpuConsumption": self.cpu_consumption,
            "failedCpuConsumption": self.failed_cpu_consumption,
            "expectedCpuConsumption": self.expected_cpu_consumption,
            "realConsumption": self.real_consumption,
            "failedRealConsumption": timedelta2hours(self.failed_run_time),
            "expectedConsumption": self.expected_real_consumption,
            "retrialCount": self.retrial_count,
            "submittedCount": self.retrial_count,
            "completedCount": self.completed_retrial_count,
            "failedCount": self.failed_retrial_count
        }


class Statistics(object):

    def __init__(self, jobs, start, end, queue_time_fix):
        """
        """
        self._jobs = jobs
        self._start = start
        self._end = end
        self._queue_time_fixes = queue_time_fix
        self._name_to_jobStat_dict = dict()

    def _calculate_statistics(self):
        for index, job in enumerate(self._jobs):
            retrials = job.get_last_retrials()
            for retrial in retrials:
                job_stat = self._name_to_jobStat_dict.setdefault(
                    job.name, JobStat(job.name, job.total_processors, job.total_wallclock))
                job_stat.inc_retrial_count()
                if Job.is_a_completed_retrial(retrial):
                    job_stat.inc_completed_retrial_count()
                    submit_time = retrial[0]
                    start_time = retrial[1]
                    finish_time = retrial[2]
                    adjusted_queue = max(start_time - submit_time, datetime.timedelta(
                    )) - datetime.timedelta(seconds=self._queue_time_fixes.get(job.name, 0))
                    job_stat.completed_queue_time += max(
                        adjusted_queue, datetime.timedelta())
                    job_stat.completed_run_time += max(
                        finish_time - start_time, datetime.timedelta())
                else:
                    job_stat.inc_failed_retrial_count()
                    submit_time = retrial[0] if len(retrial) >= 1 else None
                    start_time = retrial[1] if len(retrial) >= 2 else None
                    finish_time = retrial[2] if len(retrial) >= 3 else None
                    if finish_time and start_time:
                        job_stat.failed_run_time += max(finish_time - start_time,
                                                        datetime.timedelta())
                    if start_time and submit_time:
                        adjusted_failed_queue = max(
                            start_time - submit_time, datetime.timedelta()) - datetime.timedelta(seconds=self._queue_time_fixes.get(job.name, 0))
                        job_stat.failed_queue_time += max(adjusted_failed_queue,
                                                          datetime.timedelta())
        return list(self._name_to_jobStat_dict.values())

    def get_statistics(self):
        job_stat_list = self._calculate_statistics()
        return {
            "Period": {"From": str(self._start), "To": str(self._end)},
            "JobStatistics": [job.get_as_dict() for job in job_stat_list]
        }

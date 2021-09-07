from datetime import datetime,date
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

#https://www.jianshu.com/p/4f5305e220f0

class APSchedulerServiceClass():
    def __init__(self, showLog=False):
        self.blockingScheduler = BlockingScheduler()
        self.backgroundScheduler = BackgroundScheduler()
        self.blockingRecodeDic = {}
        self.backgroundRecodeDic = {}
        self.blockingRecodeIndex = 0
        self.backgroundRecodeIndex = 0
        self.showLog = showLog

    def AddJob_FixedTime(self, job_function, run_date, args=None, kwargs=None, timezone=None, isBackground=True, jobId=None):
        '''
        添加调度器【固定时间任务】

        参数                                说明
        job_function                        事件
        run_date (datetime 或 str)          作业的运行日期或时间 date(2009, 11, 6)，datetime(2009, 11, 6, 16, 30, 5)，'2009-11-06 16:30:05'
        args                                参数
        timezone (datetime.tzinfo 或str)    时区
        jitter (int)                        振动弧度，执行时给个随机时间值，防止峰值
        '''
        jobId, sched = self._CheckGetSchedAndId(isBackground, jobId)
        if not jobId or not sched:
            return False
        job = sched.add_job(job_function, 'date', args=args, kwargs=kwargs, run_date=run_date, timezone=timezone, id=jobId)
        return self.OnAddSchedInfo(jobId, job)

    def AddJob_Interval(self, job_function, args=None, kwargs=None, weeks=0, days=0, hours=0, minutes=0, seconds=0, start_date=None, end_date=None, timezone=None, isBackground=True, jobId=None):
        '''
        添加调度器【周期触发任务】

        参数                                说明
        job_function                        事件
        args                                参数
        weeks (int)                         间隔几周
        days (int)                          间隔几天
        hours (int)                         间隔几小时
        minutes (int)                       间隔几分钟
        seconds (int)                       间隔多少秒
        start_date (datetime 或 str)        开始日期
        end_date (datetime 或 str)          结束日期
        timezone (datetime.tzinfo 或str)    时区
        jitter (int)                        振动弧度，执行时给个随机时间值，防止峰值
        '''
        jobId, sched = self._CheckGetSchedAndId(isBackground, jobId)
        if not jobId or not sched:
            return False
        job = sched.add_job(job_function, 'interval', args=args, kwargs=kwargs, weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds, start_date=start_date, end_date=end_date, timezone=timezone, id=jobId)
        return self.OnAddSchedInfo(jobId, job)

    def AddJob_Cron(self, job_function, args=None, kwargs=None, year=0, month=0, day=0, week=0, day_of_week=0, hour=0, minute=0, second=0, start_date=None, end_date=None, timezone=None, isBackground=True, jobId=None):
        '''
        添加调度器【特定周期触发任务】

        参数                                说明
        job_function                        事件
        args                                参数
        year (int 或 str)                   年，4位数字
        month (int 或 str)                  月 (范围1-12)
        day (int 或 str)                    日 (范围1-31
        week (int 或 str)                   周 (范围1-53)
        day_of_week (int 或 str)            周内第几天或者星期几 (范围0-6 或者 mon,tue,wed,thu,fri,sat,sun)
        hour (int 或 str)                   时 (范围0-23)
        minute (int 或 str)                 分 (范围0-59)
        second (int 或 str)                 秒 (范围0-59)
        start_date (datetime 或 str)        最早开始日期(包含)
        end_date (datetime 或 str)          最晚结束时间(包含)
        timezone (datetime.tzinfo 或str)    指定时区
        jitter (int)                        振动弧度，执行时给个随机时间值，防止峰值

        上面str表达式类型
        表达式     参数类型        描述
        *           所有        通配符。例：minutes=*即每分钟触发
        */a         所有        可被a整除的通配符。
        a-b         所有        范围a-b触发
        a-b/c       所有        范围a-b，且可被c整除时触发
        xth y       日          第几个星期几触发。x为第几个，y为星期几
        last x      日          一个月中，最后个星期几触发
        last        日          一个月最后一天触发
        x,y,z       所有        组合表达式，可以组合确定值或上方的表达式

        '''
        jobId, sched = self._CheckGetSchedAndId(isBackground, jobId)
        if not jobId or not sched:
            return False
        job = sched.add_job(job_function, 'cron', args=args, kwargs=kwargs, year=year, month=month, day=day, week=week, day_of_week=day_of_week, hour=hour, minute=minute, second=second, start_date=start_date, end_date=end_date, timezone=timezone, id=jobId)
        return self.OnAddSchedInfo(jobId, job)

    def RemoveJob(self, jobId='', isAll=False, isBackground=True):
        if isBackground:
            if isAll:
                for item in self.backgroundRecodeDic:
                    if self.backgroundScheduler.get_job(item):
                        self.backgroundScheduler.remove_job(item)
                self.backgroundScheduler.remove_all_jobs()
                self.backgroundRecodeDic.clear()
                self._Log("移除all：%s"%isAll)
            else:
                self.backgroundScheduler.remove_job(jobId)
                self.backgroundRecodeDic.pop(jobId)
                self._Log("移除jobId：%s"%jobId)
            if self.showLog:
                self.backgroundScheduler.print_jobs()
        else:
            if isAll:
                for item in self.blockingRecodeDic:
                    if self.blockingScheduler.get_job(item):
                        self.blockingScheduler.remove_job(item)
                self.blockingScheduler.remove_all_jobs()
                self.blockingRecodeDic.clear()
                self._Log("移除all：%s"%isAll)
            else:
                self.blockingScheduler.remove_job(jobId)
                self.blockingRecodeDic.pop(jobId)
                self._Log("移除jobId：%s"%jobId)
            if self.showLog:
                self.blockingScheduler.print_jobs()
    
    def PauseJob(self, jobId='', isAll=False, isBackground=True):
        '''暂停运行任务'''
        if isBackground:
            if isAll:
                for item in self.backgroundRecodeDic:
                    if self.backgroundScheduler.get_job(item):
                        self.backgroundScheduler.pause_job(item)
                self.backgroundScheduler.pause()
            else:
                self.backgroundScheduler.pause_job(jobId)
        else:
            if isAll:
                for item in self.blockingRecodeDic:
                    if self.backgroundScheduler.get_job(item):
                        self.backgroundScheduler.pause_job(item)
                self.blockingScheduler.pause()
            else:
                self.blockingScheduler.pause_job(jobId)

    def ResumeJob(self, jobId, isAll=False, isBackground=True):
        '''重新/继续运行任务'''
        if isBackground:
            if isAll:
                for item in self.backgroundRecodeDic:
                    if self.backgroundScheduler.get_job(item):
                        self.backgroundScheduler.resume_job(item)
                self.backgroundScheduler.resume()
            else:
                self.backgroundScheduler.resume_job(jobId)
        else:
            if isAll:
                for item in self.blockingRecodeDic:
                    if self.blockingScheduler.get_job(item):
                        self.blockingScheduler.resume_job(item)
                self.blockingScheduler.resume()
            else:
                self.blockingScheduler.resume_job(jobId)

    def Run(self, isRunBackgroundScheduler, isRunBlockingScheduler):
        if isRunBackgroundScheduler:
            if not self.backgroundScheduler.running:
                self.backgroundScheduler.start()
            else:
                self._Log("backgroundScheduler 正在运行")
                if self.showLog:
                    self.backgroundScheduler.print_jobs()
        if isRunBlockingScheduler:
            if not self.blockingScheduler.running:
                self.blockingScheduler.start()
            else:
                self._Log("blockingScheduler 正在运行")
                if self.showLog:
                    self.blockingScheduler.print_jobs()
    
    def _CheckGetSchedAndId(self, isBackground=True, jobId=None):
        '''根据 id 和 状态 判断'''
        sched = False
        if isBackground:
            if jobId:
                if jobId in self.backgroundRecodeDic:
                    print('该已存在于定时器中')
                    return False, False
            else:
                jobId = self.backgroundRecodeIndex + 1
            self.backgroundRecodeIndex += 1
            sched = self.backgroundScheduler
        else:
            if jobId:
                if jobId in self.blockingRecodeDic:
                    print('该已存在于定时器中')
                    return False, False
            else:
                jobId = self.blockingRecodeIndex + 1
            self.blockingRecodeIndex += 1
            sched = self.blockingScheduler
        return str(jobId), sched

    def OnAddSchedInfo(self, jobId, job, isBackground=True):
        '''记录定时器到字典'''
        if isBackground:
            if jobId in self.backgroundRecodeDic:
                print('该已存在于定时器中')
                return False
            self.backgroundRecodeDic[jobId] = job
        else:
            if jobId in self.blockingRecodeDic:
                print('该已存在于定时器中')
                return False
            self.blockingRecodeDic[jobId] = job
        return (jobId, job)

    def _Log(self, value):
        if self.showLog:
            print(value)

if __name__ == "__main__":
    def Test(x):
        print('Log %s'%x)
    apSchedulerService = APSchedulerServiceClass()
    print(apSchedulerService.AddJob_Interval(Test, args=[0],seconds=10))
    print(apSchedulerService.AddJob_Interval(Test, args=[1],seconds=10))
    print(apSchedulerService.AddJob_Interval(Test, args=['33'],seconds=10,jobId='33'))
    apSchedulerService.Run(True, False)
    import time 
    time.sleep(30)
    apSchedulerService.RemoveJob('1')
    apSchedulerService.RemoveJob('2')
    apSchedulerService.RemoveJob('33')
    apSchedulerService.RemoveJob('',True)
    time.sleep(30)
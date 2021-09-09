import os
from datetime import datetime

# job report content types
ContentTypeZip = 'zip'
ContentTypeGZip = 'gzip'
ContentTypeHtml = 'html'
ContentTypeJson = 'json'
ContentTypeXml = 'xml'

# default job reports name
JobReportCodeCoverage = "Code Coverage"
JobReportTests = "Tests"

JobTriggerScheduler = "SCHEDULER"
JobTriggerApi = "API"
JobTriggerManual = "MANUAL"
JobTriggerPush = "PUSH"
JobTriggerPrOpen = "PR_OPENED"
JobTriggerPrMerged = "PR_MERGED"
JobTriggerTag = "TAG"

ServerUrl = os.environ.get('FLOWCI_SERVER_URL')
FlowName = os.environ.get("FLOWCI_FLOW_NAME")

JobBuildNumber = os.environ.get("FLOWCI_JOB_BUILD_NUM")
JobStatus = os.environ.get("FLOWCI_JOB_STATUS")
JobTrigger = os.environ.get("FLOWCI_JOB_TRIGGER")
JobTriggerBy = os.environ.get("FLOWCI_JOB_TRIGGER_BY")
JobStartAt = os.environ.get("FLOWCI_JOB_START_AT")
JobFinishAt = os.environ.get("FLOWCI_JOB_FINISH_AT")
JobSteps = os.environ.get("FLOWCI_JOB_STEPS")

AgentToken = os.environ.get('FLOWCI_AGENT_TOKEN')
AgentWorkspace = os.environ.get('FLOWCI_AGENT_WORKSPACE')
AgentJobDir = os.environ.get('FLOWCI_AGENT_JOB_DIR')

GitEvent = os.environ.get('FLOWCI_GIT_EVENT')

GitCommitBranch = os.environ.get('FLOWCI_GIT_BRANCH')
GitCommitID = os.environ.get('FLOWCI_GIT_COMMIT_ID')
GitCommitMessage = os.environ.get('FLOWCI_GIT_COMMIT_MESSAGE')
GitCommitTime = os.environ.get('FLOWCI_GIT_COMMIT_TIME')
GitCommitURL = os.environ.get('FLOWCI_GIT_COMMIT_URL')

GitPrTitle = os.environ.get('FLOWCI_GIT_PR_TITLE')
GitPrMessage = os.environ.get('FLOWCI_GIT_PR_MESSAGE')
GitPrURL = os.environ.get('FLOWCI_GIT_PR_URL')
GitPrTime = os.environ.get('FLOWCI_GIT_PR_TIME')
GitPrNumber = os.environ.get('FLOWCI_GIT_PR_NUMBER')

GitPrHeadRepoName = os.environ.get('FLOWCI_GIT_PR_HEAD_REPO_NAME')
GitPrHeadRepoBranch = os.environ.get('FLOWCI_GIT_PR_HEAD_REPO_BRANCH')
GitPrHeadRepoCommit = os.environ.get('FLOWCI_GIT_PR_HEAD_REPO_COMMIT')

GitPrBaseRepoName = os.environ.get('FLOWCI_GIT_PR_BASE_REPO_NAME')
GitPrBaseRepoBranch = os.environ.get('FLOWCI_GIT_PR_BASE_REPO_BRANCH')
GitPrBaseRepoCommit = os.environ.get('FLOWCI_GIT_PR_BASE_REPO_COMMIT')


class Job:
    def __init__(self):
        self.flowName = FlowName
        self.number = JobBuildNumber
        self.status = JobStatus
        self.trigger = JobTrigger
        self.triggerBy = JobTriggerBy
        self.startAt = JobStartAt
        self.finishAt = JobFinishAt
        self.duration = "-"
        self.steps = []

        self.gitCommit = GitCommit()
        self.gitPr = GitPr()

        if self.hasValue(JobStartAt) and self.hasValue(JobFinishAt):
            start = datetime.strptime(JobStartAt, "%Y-%m-%d %H:%M:%S.%f")
            finish = datetime.strptime(JobFinishAt, "%Y-%m-%d %H:%M:%S.%f")
            self.duration = abs(finish - start).microseconds

        if self.hasValue(JobSteps):
            items = JobSteps.split(";")
            for item in items:
                if item != '':
                    self.steps.append(Step(item))

    def hasValue(self, val):
        return val != None and val != ''


class Step:
    def __init__(self, strItem):
        pair = strItem.split("=")
        self.name = pair[0]
        self.status = pair[1]


class GitCommit:
    def __init__(self):
        self.id = GitCommitID
        self.branch = GitCommitBranch
        self.message = GitCommitMessage
        self.time = GitCommitTime
        self.url = GitCommitURL


class GitPr:
    def __init__(self):
        self.title = GitPrTitle
        self.message = GitPrMessage
        self.url = GitPrURL
        self.number = GitPrNumber
        self.time = GitPrTime
        self.head = GitPrHeadRepo()
        self.base = GitPrBaseRepo()


class GitPrHeadRepo:
    def __init__(self):
        self.name = GitPrHeadRepoName
        self.branch = GitPrHeadRepoBranch
        self.commit = GitPrHeadRepoCommit


class GitPrBaseRepo:
    def __init__(self):
        self.name = GitPrBaseRepoName
        self.branch = GitPrBaseRepoBranch
        self.commit = GitPrBaseRepoCommit

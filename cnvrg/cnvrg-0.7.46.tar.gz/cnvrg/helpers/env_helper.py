import os

EXPERIMENT = "Experiment"
ENDPOINT = "Endpoint"

ENV_KEYS = {
    "current_job_id": "CNVRG_JOB_ID",
    "current_job_type": "CNVRG_JOB_TYPE",
    "current_project": "CNVRG_PROJECT",
    "current_organization": "CNVRG_OWNER"
}

POOL_SIZE = os.environ.get("CNVRG_THREAD_SIZE") or 20
CURRENT_JOB_ID = os.environ.get("CNVRG_JOB_ID")
CURRENT_JOB_TYPE = os.environ.get("CNVRG_JOB_TYPE")
CNVRG_OUTPUT_DIR = os.environ.get("CNVRG_OUTPUT_DIR")
CURRENT_PROJECT_SLUG = os.environ.get(ENV_KEYS["current_project"])
CURRENT_ORGANIZATION_SLUG = os.environ.get(ENV_KEYS["current_organization"])
MAX_LOGS_PER_SEND = int(os.environ.get("CNVRG_MAX_LOGS_PER_SEND") or 500)

def in_experiment():
    return os.environ.get("CNVRG_JOB_TYPE") == EXPERIMENT

def get_current_job_id():
    return os.environ.get("CNVRG_JOB_ID")

def get_current_job_type():
    return os.environ.get("CNVRG_JOB_TYPE")

def set_current_job_id(job_id):
    os.environ["CNVRG_JOB_ID"] = job_id

def set_current_job_type(job_slug):
    os.environ["CNVRG_JOB_TYPE"] = job_slug

def get_origin_job():
    current_job_id = get_current_job_id()
    current_job_type = get_current_job_type()
    if not current_job_id and not current_job_type: return {}
    return {
        "origin_job_id": current_job_id,
        "origin_job_type": current_job_type
    }
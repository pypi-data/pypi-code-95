import requests

CONFIG = {
    "LOCAL": {
        "LOCAL": {
            "TEST_URL": "http://127.0.0.1:8080",
            "LUNAR_REC_URL": "http://127.0.0.1:8080",
            "LUNAR_DATA_URL": "http://127.0.0.1:8080",
        },
    },
    "DEV": {
        "LOCAL": {
            "TEST_URL": "https://rec.dev.apollo-lunar.com",
            "LUNAR_REC_URL": "https://rec.dev.apollo-lunar.com",
            "LUNAR_DATA_URL": "https://data.dev.apollo-lunar.com",
        },
        "LUNAR": {
            "TEST_URL": "https://a3hugleaz2-vpce-03604adfb32e11eeb.execute-api.ap-northeast-2.amazonaws.com",
            "LUNAR_REC_URL": "https://a3hugleaz2-vpce-03604adfb32e11eeb.execute-api.ap-northeast-2.amazonaws.com",
            "LUNAR_DATA_URL": "https://3fp7y22d53-vpce-03604adfb32e11eeb.execute-api.ap-northeast-2.amazonaws.com",
        },
    },
    "STG": {
        "EDD": {
            "TEST_URL": "http://150.6.13.63:8081",
            "LUNAR_REC_URL": "https://qlcw33mp1g-vpce-00c2fe2f2b87f7ade.execute-api.ap-northeast-2.amazonaws.com",
            "LUNAR_DATA_URL": "https://fqo6ikf8vg-vpce-00c2fe2f2b87f7ade.execute-api.ap-northeast-2.amazonaws.com",
            "COPY_DATABASE_URL": "http://150.6.13.9:31771/edd_to_lunar/copy_database",
            "COPY_FILES_URL": "http://150.6.13.9:31771/edd_to_lunar/copy_files",
            "JOB_STATUS_URL": "http://150.6.13.9:31771/edd_to_lunar/job_status",
        },
        "LOCAL": {
            "TEST_URL": "https://rec.stg.apollo-lunar.com",
            "LUNAR_REC_URL": "https://rec.stg.apollo-lunar.com",
            "LUNAR_DATA_URL": "https://data.stg.apollo-lunar.com",
        },
        "LUNAR": {
            "TEST_URL": "https://qlcw33mp1g-vpce-00c2fe2f2b87f7ade.execute-api.ap-northeast-2.amazonaws.com",
            "LUNAR_REC_URL": "https://qlcw33mp1g-vpce-00c2fe2f2b87f7ade.execute-api.ap-northeast-2.amazonaws.com",
            "LUNAR_DATA_URL": "https://fqo6ikf8vg-vpce-00c2fe2f2b87f7ade.execute-api.ap-northeast-2.amazonaws.com",
        },
    },
    "PRD": {
        "EDD": {
            "TEST_URL": "http://150.6.13.63:8081",
            "LUNAR_REC_URL": "https://x0eucmpwcd-vpce-02ba2f7cd263a45a1.execute-api.ap-northeast-2.amazonaws.com",
            "LUNAR_DATA_URL": "https://b9xs1lvk5c-vpce-02ba2f7cd263a45a1.execute-api.ap-northeast2.amazonaws.com/api",
            "COPY_DATABASE_URL": "http://150.6.13.9:31771/edd_to_lunar/copy_database",
            "COPY_FILES_URL": "http://150.6.13.9:31771/edd_to_lunar/copy_files",
            "JOB_STATUS_URL": "http://150.6.13.9:31771/edd_to_lunar/job_status",
        },
        "LOCAL": {
            "TEST_URL": "https://rec.apollo-lunar.com",
            "LUNAR_REC_URL": "https://rec.apollo-lunar.com",
            "LUNAR_DATA_URL": "https://data.apollo-lunar.com",
        },
        "LUNAR": {
            "TEST_URL": "https://x0eucmpwcd-vpce-02ba2f7cd263a45a1.execute-api.ap-northeast-2.amazonaws.com",
            "LUNAR_REC_URL": "https://x0eucmpwcd-vpce-02ba2f7cd263a45a1.execute-api.ap-northeast-2.amazonaws.com",
            "LUNAR_DATA_URL": "https://b9xs1lvk5c-vpce-02ba2f7cd263a45a1.execute-api.ap-northeast2.amazonaws.com/api",
        },
    },
}


class Config:
    def __init__(self, env: str, apikey: str):
        assert env in CONFIG.keys(), f"`env` must be in {CONFIG.keys()}"

        setattr(self, "ENV", env)
        setattr(self, "APIKEY", apikey)

        for runtime_env, urls in CONFIG.get(env).items():
            try:
                requests.get(url=urls["TEST_URL"], timeout=0.1)
                setattr(self, "RUNTIME_ENV", runtime_env)
                for key, url in urls.items():
                    setattr(self, key, url)
                break
            except Exception:
                continue

        if not hasattr(self, "RUNTIME_ENV"):
            raise Exception(f"Lunar {env} does not support this runtime environment.")

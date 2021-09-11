import subprocess, os
import pandas as pd


class Configure:
    """
    Set up GCP VMs according to the template & settings
    """
    def __init__(self, Path, GCPConfig, container_zone='eu'):
        self.path, self.cnf = Path, GCPConfig
        self.gcp_template = open(self.path.CREATE_GCP_TEMPLATE).read()
        self.container_zone = container_zone

    def create_template(self, prefix, docker_image, rq_name, cmd, machine_type, container_count=2,
                        preemptible=True, timeout=None):
        def get_startup_script():
            return startup_script.replace('$HOST_IP', self.cnf.HOST_IP
                                          ).replace('$PASSWD', self.cnf.PASSWD
                                                    ).replace('$IMAGE',
                                                              f"{self.container_zone}.gcr.io/{self.cnf.GCP_PROJECT}/{docker_image}"
                                                              ).replace('$REDIS_QUEUE_NAME', rq_name
                                                                        ).replace('$CMD', cmd)

        startup_script = open(self.path.STARTUP_SCRIPT).read()
        startup_script = get_startup_script()
        startup_script = ' && '.join([startup_script for _ in range(container_count)])
        cleanup = 'docker rm $(docker ps -aq) -f && '
        startup_script = cleanup + startup_script
        query = self.gcp_template.replace('$GCP_PROJECT', self.cnf.GCP_PROJECT
                                     ).replace('$TEMPLATE_NAME', f"{prefix}-template"
                                               ).replace('$IMAGE', f"{self.container_zone}.gcr.io/{self.cnf.GCP_PROJECT}/{docker_image}"
                                                         ).replace('$SERVICE_ACCOUNT', self.cnf.SERVICE_ACCOUNT
                                                                   ).replace(
            '$STARTUP_SCRIPT', f"'{startup_script}'").replace('$MACHINE_TYPE', machine_type)
        if not preemptible:
            query = query.replace('--preemptible', '').replace('--maintenance-policy=TERMINATE',
                                                               '--maintenance-policy=MIGRATE')
        if timeout is not None:
            query = query.replace('REDIS_TIMEOUT_SECOND=10', f"REDIS_TIMEOUT_SECOND={int(timeout)}")
        print(query)
        os.system(query)

    def create_vm(self, prefix, vm_count=3):
        names = ' '.join([f"{prefix}-{i}" for i in range(1, vm_count + 1)])
        template = f"{prefix}-template"
        query = f"gcloud beta compute instances create {names} --zone us-central1-f --source-instance-template {template}"
        print(query)
        out = subprocess.Popen(query.replace('\\', '').split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        print(stdout.decode().split('\n')[5:-1])

    def fmt_vm_cnf(self, df, to_skip=('master',)):
        for _, row in df.iterrows():
            if row.prefix in to_skip:
                print('skipped: ', row.pipeline_name, row.prefix)
                continue
            else:
                print('working on: ', row.prefix)
            self.create_template(row.prefix, row.docker_image, row.rq_name, row.cmd, row.machine_type,
                                 container_count=row.container_count,
                                 preemptible=row.is_preemptible)  # , timeout=row.rq_timeout
            self.create_vm(row.prefix, vm_count=row.machine_count)
            print('\n####')

    def set_up(self, pipeline_name=None):
        # TODO: wipe-out existent conflicting infrastructure
        infrastructure = pd.read_json(self.path.VM_SETTINGS).T
        if pipeline_name is not None:
            infrastructure = infrastructure.query(f"pipeline_name=='{pipeline_name}'")
        self.fmt_vm_cnf(infrastructure.fillna(''))

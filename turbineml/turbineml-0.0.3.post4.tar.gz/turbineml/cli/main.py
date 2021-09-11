import argparse
from turbineml import __version__
from turbineml.configuration import _config
from turbineml.jobs import JobConfiguration, create_job
import yaml
import os

def main():
    parser = argparse.ArgumentParser(description='Turbine ML')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    subparsers = parser.add_subparsers(dest="command", required=True)

    configure_parser = subparsers.add_parser("configure")
    configure_parser.add_argument("--set-api-key", default=None, help="Set the default API key for the current user")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("configuration", default=None, help="Path to the configuration file for the job")

    args = parser.parse_args()

    if args.command == "configure":
        if args.set_api_key is not None:
            _config.set_api_key(args.set_api_key)
    
    if args.command == "run":
        config_path = os.path.abspath(args.configuration)
        job_dir = os.path.dirname(config_path)

        with open(config_path, 'r') as f:
            parsed = yaml.safe_load(f)
        project = parsed["project"]
        name = parsed["name"]
        config = JobConfiguration.from_object(parsed)
        
        job = create_job(project, name)
        job.set_configuration(config)
        job.upload_code_archive(job_dir)
        job.enqueue()
        print(job.job_id)

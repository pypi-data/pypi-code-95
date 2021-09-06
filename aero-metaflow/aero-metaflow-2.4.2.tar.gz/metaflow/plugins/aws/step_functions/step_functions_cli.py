import base64
import click
from hashlib import sha1
import json
import re
from distutils.version import LooseVersion
from datetime import datetime

from metaflow import current, decorators, parameters, JSONType
from metaflow.metaflow_config import SFN_STATE_MACHINE_PREFIX
from metaflow.exception import MetaflowException, MetaflowInternalError
from metaflow.datastore.datastore import TransformableObject
from metaflow.package import MetaflowPackage
from metaflow.plugins import BatchDecorator
from metaflow.util import get_username, to_bytes, to_unicode

from .step_functions import StepFunctions
from .production_token import load_token, store_token, new_token

VALID_NAME = re.compile('[^a-zA-Z0-9_\-\.]')
BACK_KEYWORD = "Back"
EXIT_KEYWORD = "Exit"

class IncorrectProductionToken(MetaflowException):
    headline = "Incorrect production token"

class IncorrectMetadataServiceVersion(MetaflowException):
    headline = "Incorrect version for metaflow service"

class StepFunctionsStateMachineNameTooLong(MetaflowException):
    headline = "AWS Step Functions state machine name too long"

@click.group()
def cli():
    pass

@cli.group(help="Commands related to scheduling Aero Flows.")
@click.option('--name',
              default=None,
              type=str,
              help="State Machine name. The flow name is used instead "
                   "if this option is not specified")
@click.pass_obj
def schedule(obj, name=None):
    obj.check(obj.graph, obj.flow, obj.environment, pylint=obj.pylint)
    obj.state_machine_name, obj.token_prefix, obj.is_project = \
                                      resolve_state_machine_name(obj, name)

@schedule.command(help="Deploy a new version of this workflow to "
                    "the Aero scheduler.")
@click.option('--authorize',
              default=None,
              help="Authorize using this production token. You need this "
                   "when you are re-deploying an existing flow for the first "
                   "time. The token is cached in METAFLOW_HOME, so you only "
                   "need to specify this once.")
@click.option('--generate-new-token',
              is_flag=True,
              help="Generate a new production token for this flow. "
                   "This will move the production flow to a new "
                   "namespace.")
@click.option('--new-token',
              'given_token',
              default=None,
              help="Use the given production token for this flow. "
                   "This will move the production flow to the given "
                   "namespace.")
@click.option('--tag',
              'tags',
              multiple=True,
              default=None,
              help="Annotate all objects produced by scheduling Aero Flows "
                   "with the given tag. You can specify this option multiple "
                   "times to attach multiple tags.")
@click.option('--namespace',
              'user_namespace',
              default=None,
              help="Change the namespace from the default (production token) "
                   "to the given tag. See run --help for more information.")
@click.option('--only-json',
              is_flag=True,
              default=False,
              help="Only print out JSON sent to the Aero scheduler. Do not "
                   "deploy anything.")
@click.option('--max-workers',
              default=100,
              show_default=True,
              help="Maximum number of parallel processes.")
@click.option('--workflow-timeout',
              default=None,
              type=int,
              help="Workflow timeout in seconds.")
@click.option('--log-execution-history',
              is_flag=True,
              help="Log AWS Step Functions execution history to AWS CloudWatch "
                   "Logs log group.")
@click.pass_obj
def create(obj,
           tags=None,
           user_namespace=None,
           only_json=False,
           authorize=None,
           generate_new_token=False,
           given_token=None,
           max_workers=None,
           workflow_timeout=None,
           log_execution_history=False):
    obj.echo("Deploying *%s* to AWS Step Functions..." % obj.state_machine_name,
             bold=True)

    check_metadata_service_version(obj)

    token = resolve_token(obj.state_machine_name,
                          obj.token_prefix,
                          obj,
                          authorize,
                          given_token,
                          generate_new_token,
                          obj.is_project)

    flow = make_flow(obj,
                     token,
                     obj.state_machine_name,
                     tags,
                     user_namespace,
                     max_workers,
                     workflow_timeout,
                     obj.is_project)

    if only_json:
        obj.echo_always(flow.to_json(), err=False, no_bold=True)
    else:
        flow.deploy(log_execution_history)
        obj.echo("State Machine *{state_machine}* "
                 "for flow *{name}* pushed to "
                 "AWS Step Functions successfully.\n"
                    .format(state_machine=obj.state_machine_name,
                            name=current.flow_name), 
                 bold=True)
        if obj._is_state_machine_name_hashed:
            obj.echo("Note that the flow was deployed with a truncated name "
                     "due to a length limit on AWS Step Functions. The "
                     "original long name is stored in task metadata.\n")
        flow.schedule()
        obj.echo("What will trigger execution of the workflow:", bold=True)
        obj.echo(flow.trigger_explanation(), indent=True)
        

def check_metadata_service_version(obj):
    return

def resolve_state_machine_name(obj, name):
    def attach_prefix(name):
      if SFN_STATE_MACHINE_PREFIX is not None:
          return SFN_STATE_MACHINE_PREFIX + '_' + name
      return name
    project = current.get('project_name')
    obj._is_state_machine_name_hashed = False
    if project:
        if name:
            raise MetaflowException("--name is not supported for @projects. "
                                    "Use --branch instead.")
        state_machine_name = attach_prefix(current.project_flow_name)
        project_branch = to_bytes('.'.join((project, current.branch_name)))
        token_prefix = 'mfprj-%s' % to_unicode(
                                        base64.b32encode(
                                            sha1(project_branch).digest()))[:16]
        is_project = True
        # AWS Step Functions has a limit of 80 chars for state machine names.
        # We truncate the state machine name if the computed name is greater
        # than 60 chars and append a hashed suffix to ensure uniqueness.
        if len(state_machine_name) > 60:
            name_hash = to_unicode(
                            base64.b32encode(
                                sha1(to_bytes(state_machine_name)) \
                                  .digest()))[:16].lower()
            state_machine_name =\
                '%s-%s' % (state_machine_name[:60], name_hash)
            obj._is_state_machine_name_hashed = True
    else:
        if name and VALID_NAME.search(name):
            raise MetaflowException(
                "Name '%s' contains invalid characters." % name)

        state_machine_name = attach_prefix(name if name else current.flow_name)
        token_prefix = state_machine_name
        is_project = False

        if len(state_machine_name) > 80:
            msg = "The full name of the workflow:\n*%s*\nis longer than 80 "\
                  "characters.\n\n"\
                  "To deploy this workflow to AWS Step Functions, please "\
                  "assign a shorter name\nusing the option\n"\
                  "*step-functions --name <name> create*." % state_machine_name
            raise StepFunctionsStateMachineNameTooLong(msg)

    return state_machine_name, token_prefix.lower(), is_project

def make_flow(obj,
              token,
              name,
              tags,
              namespace,
              max_workers,
              workflow_timeout,
              is_project):
    datastore = obj.datastore(obj.flow.name,
                              mode='w',
                              metadata=obj.metadata,
                              event_logger=obj.event_logger,
                              monitor=obj.monitor)
    if datastore.TYPE != 's3':
        raise MetaflowException("Aero scheduler requires --datastore=s3.")

    # Attach AWS Batch decorator to the flow
    decorators._attach_decorators(obj.flow, [BatchDecorator.name])
    decorators._init_step_decorators(
            obj.flow, obj.graph, obj.environment, obj.datastore, obj.logger)

    obj.package = MetaflowPackage(
        obj.flow, obj.environment, obj.echo, obj.package_suffixes)
    package_url = datastore.save_data(
        obj.package.sha, TransformableObject(obj.package.blob))

    return StepFunctions(name,
                         obj.graph,
                         obj.flow,
                         obj.package,
                         package_url,
                         token,
                         obj.metadata,
                         obj.datastore,
                         obj.environment,
                         obj.event_logger,
                         obj.monitor,
                         tags=tags,
                         namespace=namespace,
                         max_workers=max_workers,
                         username=get_username(),
                         workflow_timeout=workflow_timeout,
                         is_project=is_project)

def resolve_token(name,
                  token_prefix,
                  obj,
                  authorize,
                  given_token,
                  generate_new_token,
                  is_project):

    # 1) retrieve the previous deployment, if one exists
    workflow = StepFunctions.get_existing_deployment(name)
    if workflow is None:
        obj.echo("It seems this is the first time you are deploying *%s* to "
                 "the Aero scheduler." % name)
        prev_token = None
    else:
        prev_user, prev_token = workflow

    # 2) authorize this deployment
    if prev_token is not None:
        if authorize is None:
            authorize = load_token(token_prefix)
        elif authorize.startswith('production:'):
            authorize = authorize[11:]

        # we allow the user who deployed the previous version to re-deploy,
        # even if they don't have the token
        if prev_user != get_username() and authorize != prev_token:
            obj.echo("There is an existing version of *%s* on the Aero "
                     "scheduler which was deployed by the user "
                     "*%s*." % (name, prev_user))
            obj.echo("To deploy a new version of this flow, you need to use "
                     "the same production token that they used. ")
            obj.echo("Please reach out to them to get the token. Once you "
                     "have it, call this command:")
            obj.echo("    schedule create --authorize MY_TOKEN", 
                        fg='green')
            obj.echo('See "Organizing Results" at docs.metaflow.org for more '
                     "information about production tokens.")
            raise IncorrectProductionToken("Try again with the correct "
                                           "production token.")

    # 3) do we need a new token or should we use the existing token?
    if given_token:
        if is_project:
            # we rely on a known prefix for @project tokens, so we can't
            # allow the user to specify a custom token with an arbitrary prefix
            raise MetaflowException("--new-token is not supported for "
                                    "@projects. Use --generate-new-token to "
                                    "create a new token.")
        if given_token.startswith('production:'):
            given_token = given_token[11:]
        token = given_token
        obj.echo('')
        obj.echo("Using the given token, *%s*." % token)
    elif prev_token is None or generate_new_token:
        token = new_token(token_prefix, prev_token)
        if token is None:
            if prev_token is None:
                raise MetaflowInternalError("We could not generate a new "
                                            "token. This is unexpected. ")
            else:
                raise MetaflowException("--generate-new-token option is not "
                                        "supported after using --new-token. "
                                        "Use --new-token to make a new "
                                        "namespace.")
        obj.echo('')
        obj.echo("A new production token generated.")
    else:
        token = prev_token

    obj.echo('')
    obj.echo("The namespace of this production flow is")
    obj.echo('    production:%s' % token, fg='green')
    obj.echo("To analyze results of this production flow "
             "add this line in your notebooks:")
    obj.echo('    namespace(\"production:%s\")' % token, fg='green')
    obj.echo("If you want to authorize other people to deploy new versions "
             "of this flow to the Aero scheduler, they need to call")
    obj.echo("    step-functions create --authorize %s" % token, fg='green')
    obj.echo("when deploying this flow to the Aero scheduler for the first "
             "time.")
    obj.echo('See "Organizing Results" at https://docs.metaflow.org/ for more '
             "information about production tokens.")
    obj.echo('')
    store_token(token_prefix, token)
    return token


@parameters.add_custom_parameters(deploy_mode=False)
@schedule.command(help="Trigger the workflow on the Aero scheduler.")
@click.pass_obj
def trigger(obj, **kwargs):
    def _convert_value(param):
        # Swap `-` with `_` in parameter name to match click's behavior
        val = kwargs.get(param.name.replace('-', '_').lower())
        return json.dumps(val) if param.kwargs.get('type') == JSONType else \
            val() if callable(val) else val

    params = {param.name: _convert_value(param)
              for _, param in obj.flow._get_parameters()
                if kwargs.get(param.name.replace('-', '_').lower()) is not None}

    response = StepFunctions.trigger(obj.state_machine_name, params)

    id = response['executionArn'].split(':')[-1]
    obj.echo("Workflow *{name}* triggered on AWS Step Functions "
        "(run-id *sfn-{id}*)."
            .format(name=obj.state_machine_name, id=id), bold=True)


@schedule.command(
    help="List all runs of the workflow on Aero scheduler.")
@click.option("--running", default=False, is_flag=True,
    help="List all runs of the workflow in RUNNING state on "
        "the Aero scheduler.")
@click.option("--succeeded", default=False, is_flag=True,
    help="List all runs of the workflow in SUCCEEDED state on "
        "the Aero scheduler.")
@click.option("--failed", default=False, is_flag=True,
    help="List all runs of the workflow in FAILED state on "
        "the Aero scheduler.")
@click.option("--timed-out", default=False, is_flag=True,
    help="List all runs of the workflow in TIMED_OUT state on "
        "the Aero scheduler.")
@click.option("--aborted", default=False, is_flag=True,
    help="List all runs of the workflow in ABORTED state on "
        "the Aero scheduler.")
@click.pass_obj
def list_runs(obj, 
              running=False,
              succeeded=False,
              failed=False,
              timed_out=False,
              aborted=False):
    states = []
    if running:
        states.append('RUNNING')
    if succeeded:
        states.append('SUCCEEDED')
    if failed:
        states.append('FAILED')
    if timed_out:
        states.append('TIMED_OUT')
    if aborted:
        states.append('ABORTED')
    executions = StepFunctions.list(obj.state_machine_name, states)
    found = False
    for execution in executions:
        found = True
        if execution.get('stopDate'):
            obj.echo(
                "*sfn-{id}* "
                "startedAt:'{startDate}' "
                "stoppedAt:'{stopDate}' "
                "*{status}*".format(
                    id=execution['name'], 
                    status=execution['status'], 
                    startDate=execution['startDate'].replace(microsecond=0), 
                    stopDate=execution['stopDate'].replace(microsecond=0),
                )
            )
        else:
            obj.echo(
                "*sfn-{id}* "
                "startedAt:'{startDate}' "
                "*{status}*".format(
                    id=execution['name'], 
                    status=execution['status'], 
                    startDate=execution['startDate'].replace(microsecond=0)
                )
            )
    if not found:
        if len(states) > 0:
            status = ''
            for idx, state in enumerate(states):
                if idx == 0:
                    pass
                elif idx == len(states) - 1:
                    status += ' and '
                else:
                    status += ', '
                status += '*%s*' % state
            obj.echo('No %s executions for *%s* found on AWS Step Functions.'
                % (status, obj.state_machine_name))
        else:
            obj.echo('No executions for *%s* found on AWS Step Functions.' \
                % (obj.state_machine_name))


@schedule.command(
    help="List all runs of the workflow on Aero scheduler.")
@click.option("--flow-id", default=None,
    help="List all runs of the workflow in ABORTED state on "
        "the Aero scheduler.")
@click.pass_obj
def get_logs(obj, flow_id=None):

    from ..aws_client import get_aws_client 

    # Get AWS Clients
    sfn = get_aws_client('stepfunctions')
    cloudwatch = get_aws_client('logs')

    cli_state = {
        "flow_id": obj.flow.name
    }

    # Execution (Run) > Step > Task
    question_arr = [
        ask_execution_question, 
        ask_step_question, 
        ask_task_question
    ]

    # Iterate through question array, reducing question if BACK selected
    # If question returns false, reduce question number to prevent loop
    question = 0
    while question >= 0:

        resp = question_arr[question](
            cli_state,
            sfn=sfn,
            cloudwatch=cloudwatch
        )

        # If back or 
        if resp == BACK_KEYWORD:
            question -= 1
        # If we are at the end, stay on the last question
        elif question != (len(question_arr)-1):
            question += 1


def get_key(param, key):
    try:
        lst = param['Container']['Environment']

        for elem in lst:
            if elem['Name'] == key:
                return elem['Value']

        return 0
    except:
        return 0


def build_event_tree(execution_history):

    tree = {}

    # Events are in order
    for task in execution_history['events']:

        # If task has scheduled 
        if task['type'] == "TaskScheduled":
        
            # Some intermediate tasks arent actually steps - so skip
            if task['taskScheduledEventDetails'].get('resourceType', "") == "dynamodb":
                continue

            # Get step name
            param = json.loads(task['taskScheduledEventDetails']['parameters'])
            step_name = param['Parameters']['metaflow.step_name']

            tree[step_name] = {}

        # If Succeeded
        if task['type'] == "TaskSucceeded":

            # Some intermediate tasks arent actually steps - so skip
            if task['taskSucceededEventDetails'].get('resourceType', "") == "dynamodb":
                continue

            output = json.loads(task['taskSucceededEventDetails']['output'])
            step_name = output['Parameters']['metaflow.step_name']

            # Could be a FOR step, so get the task ids for each foreach task. If not then 0.
            split_index = int(get_key(output, 'METAFLOW_SPLIT_INDEX'))

            # Tasks can be attempted multiple times, so iterate through these
            for attempt in output['Attempts']:
                
                # If split index in the step dict already
                if split_index in tree[step_name]:
                    # Add task state and logid
                    tree[step_name][split_index].append(("TaskSucceeded", attempt['Container']['LogStreamName']))
                else:
                    # Add task state and logid
                    tree[step_name][split_index] = [("TaskSucceeded", attempt['Container']['LogStreamName'])]
                    
        if task['type'] == "TaskFailed":

            if task['taskFailedEventDetails'].get('resourceType', "") == "dynamodb":
                continue

            output = json.loads(task['taskFailedEventDetails']['cause'])
            step_name = output['Parameters']['metaflow.step_name']

            split_index = int(get_key(output, 'METAFLOW_SPLIT_INDEX'))

            # Tasks can be attempted multiple times, so iterate through these
            for attempt in output['Attempts']:

                # If split index in the step dict already
                if split_index in tree[step_name]:
                    tree[step_name][split_index].append(("TaskFailed", attempt['Container']['LogStreamName']))
                else:
                    tree[step_name][split_index] = [("TaskFailed", attempt['Container']['LogStreamName'])]

    '''
        End up with:
        {
            "<step_name>": { # Step name
                0: [ # Attempt id
                    (TaskState, LogId),
                    ...
                ],
                ..
            },
            ...
        }
    '''
                    
    return tree
   

def ask_task_question(obj, cloudwatch=None, sfn=None):

    # If there is only one task (likely for most steps), open the task logs
    if len(obj['tree'][obj['step']].keys()) == 1:
        
        # fetch logs for tree[step][0][0][1]
        open_log(obj['tree'][obj['step']][0][0][1], cloudwatch)
        # If we dont BACK, then this function keeps being run, then opening logs
        # So we go back to get to step selector
        return BACK_KEYWORD

    task = ask_questions(
        f"Which Task from Step {obj['step']}?",
        [f"{obj['step']}_{i}" for i in obj['tree'][obj['step']].keys()],
        enable_back=True
    )

    if check_if_back_or_exit(task):
        return BACK_KEYWORD

    task_id = int(task.split("_")[-1])

    open_log(obj['tree'][obj['step']][task_id][0][1], cloudwatch)


def ask_step_question(obj, cloudwatch=None, sfn=None):

    execution_history = sfn.get_execution_history(
        executionArn=obj['execution_arn']
    )

    tree = build_event_tree(execution_history)

    steps = []

    # Add Failed tag to steps which have failed
    for key in tree:
        has_failed = False
        for index in tree[key]:
            for attempts in tree[key][index]:
                if attempts[0] == "TaskFailed":
                    has_failed = True
        
        steps.append(f"FAILED: {key}" if has_failed else key)

    step = ask_questions(
        f"Which Step in {obj['flow_id']}?",
        steps,
        enable_back=True
    ).replace("FAILED: ", "")

    if check_if_back_or_exit(step):
        return BACK_KEYWORD

    obj['step'] = step
    obj['tree'] = tree


def ask_execution_question(obj, cloudwatch=None, sfn=None):

    # Get all StateMachines from AWS
    functions = sfn.list_state_machines()['stateMachines']
    functions.sort(key=lambda item:item['creationDate'], reverse=True)

    def get_key(lst, key, name):

        for elem in lst:
            if elem[key] == name:
                return elem

        return None

    flow_state_machine = get_key(functions, "name", obj['flow_id'])

    executions = sfn.list_executions(
        stateMachineArn=flow_state_machine['stateMachineArn']
    )['executions']
    executions.sort(key=lambda item:item['startDate'], reverse=True)

    execution_date = ask_questions(
        f"Which execution of {obj['flow_id']}?",
        [x['startDate'] for x in executions]
    )

    if check_if_back_or_exit(execution_date):
        return BACK_KEYWORD

    execution_arn = get_key(executions, 'startDate', execution_date)['executionArn']

    obj['execution_arn'] = execution_arn


def check_if_back_or_exit(answer):

    if answer == BACK_KEYWORD:
        return True
    if answer == EXIT_KEYWORD:
        import sys
        sys.exit(0)
    
def chunked(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def generate_control_opts(i, l, enable_back=False):
    lst = [BACK_KEYWORD] if enable_back else [] 

    if i != 0:
        lst.append("Previous Page")
    if i != (l-1):
        lst.append("Next Page")
    
    lst.append(EXIT_KEYWORD)
    
    return lst

def ask_questions(question, choices, enable_back=False):
    import inquirer

    chunked_choices = chunked(choices, 8)
    i = 0

    while True:
        questions = [
            inquirer.List("var",
                        message=question,
                        choices=chunked_choices[i] + \
                            generate_control_opts(i, len(chunked_choices), enable_back),
                    ),
        ]
        response =  inquirer.prompt(questions)["var"]

        if response == "Next Page":
            i +=1
        elif response == "Previous Page":
            i -=1
        else:
            return response
        
def open_log(log_stream, cloudwatch):

    resp = cloudwatch.get_log_events(
        logGroupName="/aws/batch/job",
        logStreamName=log_stream
    )
    token = ""

    logs = resp['events']

    while token != resp['nextForwardToken']:
        token = resp['nextForwardToken']

        resp = cloudwatch.get_log_events(
            logGroupName="/aws/batch/job",
            logStreamName=log_stream,
            nextToken=token
        )
        logs.extend(resp['events'])
    
    str_logs = ""

    for log in logs:
        time = datetime.utcfromtimestamp(log['timestamp']/1000)
        str_logs += f"{time.isoformat()}: {log['message']}\n"

    import os, subprocess, tempfile

    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(str_logs)
        
        cmd = os.environ.get('EDITOR', 'vi') + ' ' + path
        subprocess.call(cmd, shell=True)
    finally:
        os.remove(path)





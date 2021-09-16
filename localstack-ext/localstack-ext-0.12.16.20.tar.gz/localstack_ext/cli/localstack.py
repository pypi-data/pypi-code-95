import os
OWuCL=True
OWuCd=False
OWuCT=None
OWuCc=Exception
OWuCD=open
OWuCv=str
OWuCV=dict
OWuCA=list
OWuCr=isinstance
import sys
from typing import Any,Callable,Dict,List
import click
from localstack.cli import LocalstackCli,LocalstackCliPlugin,console
class ProCliPlugin(LocalstackCliPlugin):
 name="pro"
 def is_active(self):
  e=os.getenv("LOCALSTACK_API_KEY")
  return OWuCL if e else OWuCd
 def attach(self,cli:LocalstackCli)->OWuCT:
  group:click.Group=cli.group
  group.add_command(cmd_login)
  group.add_command(cmd_logout)
  group.add_command(daemons)
  group.add_command(pod)
@click.group(name="daemons",help="Manage local daemon processes")
def daemons():
 pass
@click.command(name="login",help="Log in with your account credentials")
@click.option("--username",help="Username for login")
@click.option("--provider",default="internal",help="OAuth provider (default: localstack internal login)")
def cmd_login(username,provider):
 from localstack_ext.bootstrap import auth
 try:
  auth.login(provider,username)
  console.print("successfully logged in")
 except OWuCc as e:
  console.print("authentication error: %s"%e)
@click.command(name="logout",help="Log out and delete any session tokens")
def cmd_logout():
 from localstack_ext.bootstrap import auth
 try:
  auth.logout()
  console.print("successfully logged out")
 except OWuCc as e:
  console.print("logout error: %s"%e)
@daemons.command(name="start",help="Start local daemon processes")
def cmd_daemons_start():
 from localstack_ext.bootstrap import local_daemon
 console.log("Starting local daemons processes ...")
 local_daemon.start_in_background()
@daemons.command(name="stop",help="Stop local daemon processes")
def cmd_daemons_stop():
 from localstack_ext.bootstrap import local_daemon
 console.log("Stopping local daemons processes ...")
 local_daemon.kill_servers()
@daemons.command(name="log",help="Show log of daemon process")
def cmd_daemons_log():
 from localstack_ext.bootstrap import local_daemon
 file_path=local_daemon.get_log_file_path()
 if not os.path.isfile(file_path):
  console.print("no log found")
 else:
  with OWuCD(file_path,"r")as fd:
   for line in fd:
    sys.stdout.write(line)
    sys.stdout.flush()
@click.group(name="pod",help="Manage state of local cloud pods")
def pod():
 from localstack_ext.bootstrap.licensing import is_logged_in
 if not is_logged_in():
  console.print("[red]Error:[/red] not logged in, please log in first")
  sys.exit(1)
@pod.command(name="list",help="Get a list of available local cloud pods")
def cmd_pod_list():
 status=console.status("Fetching list of pods from server ...")
 status.start()
 from localstack import config
 from localstack.utils.common import format_bytes
 from localstack_ext.bootstrap import pods_client
 try:
  result=pods_client.list_pods(OWuCT)
  status.stop()
  columns={"pod_name":"Name","backend":"Backend","url":"URL","size":"Size","state":"State"}
  print_table(columns,result,formatters={"size":format_bytes})
 except OWuCc as e:
  status.stop()
  if config.DEBUG:
   console.print_exception()
  else:
   console.print("[red]Error:[/red]",e)
@pod.command(name="create",help="Create a new local cloud pod")
def cmd_pod_create():
 msg="Please head over to https://app.localstack.cloud to create a new cloud pod. (CLI support is coming soon)"
 console.print(msg)
@pod.command(name="push",help="Push the state of the LocalStack instance to a cloud pod")
@click.argument("name")
def cmd_pod_push(name:OWuCv):
 from localstack_ext.bootstrap import pods_client
 pods_client.push_state(name,OWuCT)
@pod.command(name="pull",help="Pull the state of a cloud pod into the running LocalStack instance")
@click.argument("name")
def cmd_pod_pull(name:OWuCv):
 from localstack_ext.bootstrap import pods_client
 pods_client.pull_state(name,OWuCT)
def print_table(columns:Dict[OWuCv,OWuCv],rows:List[Dict[OWuCv,Any]],formatters:Dict[OWuCv,Callable[[Any],OWuCv]]=OWuCT):
 from rich.table import Table
 if formatters is OWuCT:
  formatters=OWuCV()
 t=Table()
 for k,name in columns.items():
  t.add_column(name)
 for row in rows:
  cells=OWuCA()
  for c in columns.keys():
   cell=row.get(c)
   if c in formatters:
    cell=formatters[c](cell)
   if cell is OWuCT:
    cell=""
   if not OWuCr(cell,OWuCv):
    cell=OWuCv(cell)
   cells.append(cell)
  t.add_row(*cells)
 console.print(t)
# Created by pyminifier (https://github.com/liftoff/pyminifier)

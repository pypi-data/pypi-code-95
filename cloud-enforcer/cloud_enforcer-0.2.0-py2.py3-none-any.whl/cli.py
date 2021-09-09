"""Console script for cloud_enforcer."""
import sys
import os
import click

try:
    import cloud_enforcer.cloud_enforcer as ce
except:
    import cloud_enforcer as ce

import colorama

def OUT(outstring=''):
    '''
    Simple output printer.
    Will halt the program if it fails to write to stdout.

    Args:
        outstring: a string or anything that can become one
    Returns:
        None
    '''
    try:
        outstring = str(outstring)
    except:
        outstring = ''
    #sys.stdout.write(outstring + '\n')
    print(colorama.Fore.GREEN + outstring + colorama.Style.RESET_ALL, file=sys.stdout, flush=True)

def ERR(outstring=''):
    '''
    Simple error printer.
    Will halt the program if it fails to write to stderr.

    Args:
        outstring: a string or anything that can become one
    Returns:
        None
    '''
    try:
        outstring = str(outstring)
    except:
        outstring = ''
    #sys.stderr.write(outstring + '\n')
    print(colorama.Fore.RED + outstring + colorama.Style.RESET_ALL, file=sys.stderr, flush=True)



@click.command()
@click.option('--config', '-c', default='cloud_enforcer.yml',
    help='Specify a YAML-formatted config file')
@click.option('--ansible_tree', '-t', default="%s/ansible" % os.getenv('HOME'),
    help='Ansible tree location, ideally with an ansible.cfg .')
@click.option('--ansible_user', '-u', default='root',
    help='Remote user name.')
@click.option('--ssh_key_path', '-s', type=click.Path(), default='',
    help='SSH key location.')
@click.option('--password_file', '-f', type=click.Path(), default='',
    help='Password file location.')
@click.option('--password_prompt', '-P', type=click.BOOL, default=False,
    help='Prompt for a password.')
@click.option('--inventory_limit', '-l', default='all',
    help='Host or group run limit.')
@click.option('--playbook', '-p', default='.local/ansible/playbooks/wholecycle.yml',
    help='Host or group run limit.')
@click.option('--boot', '-n', type=click.BOOL, default=False,
    help='Allow reboots.')
#@click.argument('action')

def main(args=None):
    """Console script for cloud_enforcer."""
    click.echo("Enforcement dependencies and wrapper.")
    if password_file and password_prompt:
        ERR("You specified a password file.  Skipping password prompt.")
        password_prompt=False
    c = {}
    c['config'] = config
    c['ansible_user'] = ansible_user
    c['ssh_key_path'] = ssh_key_path
    c['password_file'] = password_file
    c['password_prompt'] = password_prompt
    c['inventory_limit'] = inventory_limit
    c['playbook'] = playbook
    c['boot'] = boot
    c['action'] = action
    ce.main(c)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

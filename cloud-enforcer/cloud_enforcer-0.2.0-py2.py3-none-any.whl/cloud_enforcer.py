"""Main module."""
import pip
import yaml
import ansible_runner
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


class LocalConfig:
    """
    Config construction.
    """
    def __init__(self, **entries):
        self.__dict__.update(entries)

def doconfig(config):
    """
    Return config object from YAML file read with '-c' parameter.
    """
    try:
        with open(config) as FH:
            configmap = yaml.safe_load(FH)
    except:
        ERR('Could not open configuration file.')
    conf = LocalConfig(**configmap)
    return(conf)

def saveconfig(config):
    """
    Save config as entered on the commandline
    """
    pass
    

def enforce(conf):
    """
    Run Ansible playbook with specified parameters.
    """
    play = ansible.runner.run(
        playbook=conf.playbook,
        inventory=conf.inventory,
        host_pattern=conf.inventory_limit,
        extravars=conf.extravars)
    OUT("{}: {}".format(play.status, play.rc))
    # successful: 0
    for each_host_event in play.events:
        OUT(each_host_event['event'])
    print("Final status:")
    print(play.stats)
    return(play)

def main(c):
    """
    Replaces previous execution with Makefiles.
    """
    os.environ['ANSIBLE_CONFIG'] = "%s/ansible.cfg" % (ansible_tree)
    conf = doconfig()
    if not 'extravars' in conf.__dict__.keys():
        conf.extravars = {}
    try:
        extravars.update(conf.extravars)
    except:
        pass
    if c.ansible_user:
        conf.ansible_user = c.ansible_user
    if c.ssh_key_path:
        conf.ssh_key_path = c.ssh_key_path
    if c.password_file:
        conf.password_file = c.password_file
    if c.password_prompt:
        conf.password_prompt = c.password_prompt
    if c.inventory_limit:
        conf.inventory_limit = c.inventory_limit
    if c.playbook:
        conf.playbook = c.playbook,
    if c.ansible_tree:
        conf.inventory = "%s/inventory" % (c.ansible_tree)
    if c.inventory_limit:
        conf.host_pattern=c.inventory_limit
    if c.boot:
        conf.extravars['accept_boot'] = c.boot

    if conf.password_file:
        try:
            with open(conf.password_file) as FH:
                conf.extravars['ansible_password'] = FH.read()
        except:
            ERR('Could not read %s' % (str(conf.password_file)))

    if conf.password_prompt:
        try:
            conf.extravars['ansible_password'] = getpass(
                "Password for %s: " % (conf.ansible_user))
        except:
            ERR('Could not parse user entry for password.')

    conf.extravars['ansible_sudo_password'] = conf.extravars['ansible_password']
    if argument == 'play':
        enforce(conf)
    elif argument == 'save':
        saveconfig(conf)
    else:
        ERR('Options are "play" or "save ," not "%s .' % (argument))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


if __name__=='__main__':
    main()

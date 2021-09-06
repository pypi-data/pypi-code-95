def get_kubectl_exec_command(
    pod_name,
    namespace,
    command,
    stdin=False,
    tty=False,
):
    kubectl_command = ['kubectl', 'exec']
    kubectl_command += ['-n', namespace]
    if stdin:
        kubectl_command += ['-i']
    if tty:
        kubectl_command += ['-t']
    kubectl_command += [pod_name]
    kubectl_command += ['--'] + list(command)
    
    return kubectl_command

def get_kubectl_logs_command(
    pod_name,
    namespace,
    follow=False,
    tail=-1,
):
    kubectl_command = ['kubectl', 'logs']
    kubectl_command += ['-n', namespace]
    if follow:
        kubectl_command += ['-f']
    kubectl_command += ['--tail', str(tail)]
    kubectl_command += [pod_name]
    
    return kubectl_command

def get_kubectl_attach_command(
    pod_name,
    namespace,
    stdin=False,
    tty=False,
):
    kubectl_command = ['kubectl', 'attach']
    kubectl_command += ['-n', namespace]
    if stdin:
        kubectl_command += ['-i']
    if tty:
        kubectl_command += ['-t']
    kubectl_command += [pod_name]
    
    return kubectl_command
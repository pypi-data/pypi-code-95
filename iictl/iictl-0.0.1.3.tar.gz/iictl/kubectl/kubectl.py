import platform
import os
import iictl

def get_executable():
    lib_path = os.path.dirname(os.path.realpath(iictl.__file__))
    
    system = platform.system()
    if system == 'Linux':
        builtin_kubectl_binary = os.path.join(lib_path, './bin/linux/kubectl')
    elif system == 'Windows':
        builtin_kubectl_binary = os.path.join(lib_path, './bin/windows/kubectl.exe')
    else:
        builtin_kubectl_binary = ''
        
    return builtin_kubectl_binary

def get_kubectl_exec_command(
    pod_name,
    namespace,
    command,
    stdin=False,
    tty=False,
    executable='kubectl',
):
    kubectl_command = [executable, 'exec']
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
    executable='kubectl',
):
    kubectl_command = [executable, 'logs']
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
    executable='kubectl',
):
    kubectl_command = [executable, 'attach']
    kubectl_command += ['-n', namespace]
    if stdin:
        kubectl_command += ['-i']
    if tty:
        kubectl_command += ['-t']
    kubectl_command += [pod_name]
    
    return kubectl_command

def get_kubectl_cp_command(
    from_path,
    to_path,
    namespace,
    executable='kubectl',
):
    kubectl_command = [executable, 'cp', '-n', namespace, from_path, to_path]
    
    return kubectl_command
from shell import Shell


class Minerva:
    @staticmethod
    def are_minerva_prerequisites_installed() -> bool:
        check_existence_in_minerva_command = "sudo kubectl exec -it deployment/minerva -c minerva -- /bin/sh -c "
        rsync_process = Shell.run(check_existence_in_minerva_command + ' "rsync"')
        openssh_process = Shell.run(check_existence_in_minerva_command + '"openssh"')
        if rsync_process.returncode != 0:
            return False
        if openssh_process.returncode != 0:
            return False
        return True

    @staticmethod
    def install_minerva_prerequisites() -> None:
        command = 'sudo kubectl exec -it deployment/minerva -c minerva -- /bin/sh -c "apk add rsync openssh"'
        Shell.run(command)

from shell import Shell


class Giove:
    @staticmethod
    def are_giove_prerequisites_installed() -> bool:
        command = 'sudo kubectl exec -it deployment/giove -c giove -- /bin/sh -c "sshpass"'
        process = Shell.run(command)
        if process.returncode != 0:
            return False
        return True

    @staticmethod
    def install_giove_prerequisites():
        command = 'sudo kubectl exec -it deployment/giove -c giove -- /bin/sh -c "dnf install sshpass"'
        Shell.run(command)

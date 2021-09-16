import click

from shell import Shell


class Container:
    @staticmethod
    def get_id(name):
        command = f"docker ps | grep {name} | grep -v istio | grep harbor | cut -d ' ' -f1"
        container_id = Shell.run(command, without_encoding=False).stdout.replace("\n", "")
        return container_id

    @staticmethod
    def check_existence(name):
        command = f"docker ps | grep harbor | grep {name}"
        result = Shell.run(command)
        if result.returncode != 0:
            click.echo(f"Invalid container name '{name}'. Please try again.")
            return

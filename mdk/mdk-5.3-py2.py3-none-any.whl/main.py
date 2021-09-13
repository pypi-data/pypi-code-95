import click
from mdk.utils import MdkBackend, VERSION


def mdk(*args, **kwargs):
    backend = MdkBackend()

    def nogpu_option(f):
        def callback(ctx, param, value):
            backend.no_gpu = value
        return click.option(
            '--nogpu',
            default=False, is_flag=True, expose_value=False,
            callback=callback)(f)

    @click.group()
    @click.version_option(version=VERSION)
    def cli():
        pass

    @cli.command(name="bash")
    @nogpu_option
    def mdk_bash():
        backend.start(implicit=True)
        backend.cmd('exec', '-it', '--env=TERM', '@CONTAINER@', 'bash')

    @cli.command(name="down")
    def mdk_down():
        backend.delete()

    @cli.command(name="exec", context_settings=dict(allow_interspersed_args=False))
    @nogpu_option
    @click.option("--interactive/--non-interactive", default=True, is_flag=True)
    @click.option("--tty/--no-tty", default=True, is_flag=True)
    @click.argument("command", nargs=-1, type=click.UNPROCESSED)
    def mdk_exec(command, interactive, tty):
        args = (
            (['--interactive'] if interactive else []) +
            (['--tty', '--env=TERM'] if tty else [])
        )
        backend.start(implicit=True)
        backend.cmd('exec', *args, '@CONTAINER@', *command)

    @cli.command(name="ls")
    @click.option("-v", "--verbose", is_flag=True)
    def mdk_ls(verbose):
        if verbose:
            backend.cmd("ps", "-a")
            backend.cmd("images")
        else:
            backend.cmd("ps", "-a", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}")
            backend.cmd("images", "--format", "table {{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}")
        backend.cmd("volume", "ls")

    @cli.command(name="lsc")
    @click.option("-v", "--verbose", is_flag=True)
    def mdk_lsc(verbose):
        cmd = ["ps", "-a"]
        if not verbose:
            cmd += ["--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}"]
        backend.cmd(*cmd)

    @cli.command(name="lsi")
    @click.option("-v", "--verbose", is_flag=True)
    def mdk_lsi(verbose):
        cmd = ["images"]
        if not verbose:
            cmd.extend(["--format", "table {{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}"])
        backend.cmd(*cmd)

    @cli.command(name="lsv")
    def mdk_lsv():
        backend.cmd("volume", "ls")

    @cli.command(name="pause")
    def mdk_pause():
        backend.cmd('pause', '@CONTAINER@', quiet=True)

    @cli.command(name="prune")
    @click.option("-v", "--volumes", is_flag=True)
    def mdk_prune(volumes):
        cmd = ["system", "prune", "--all"]
        if volumes:
            cmd.append("--volumes")
        backend.cmd(*cmd)

    @cli.command(name="rm")
    def mdk_rm():
        backend.delete()

    @cli.command(name="sh")
    @nogpu_option
    def mdk_sh():
        backend.start(implicit=True)
        backend.cmd('exec', '-it', '--env=TERM', '@CONTAINER@', 'sh')

    @cli.command(name="start")
    def mdk_start():
        backend.start()

    @cli.command(name="stop")
    def mdk_stop():
        backend.stop()

    @cli.command(name="status")
    def mdk_status():
        backend.status()

    @cli.command(name="unpause")
    def mdk_unpause():
        backend.cmd('unpause', '@CONTAINER@', quiet=True)

    @cli.command(name="up")
    @nogpu_option
    def mdk_up():
        backend.start(ensure_up_to_date=True)

    @cli.command(name="zsh")
    @nogpu_option
    def mdk_zsh():
        backend.start(implicit=True)
        backend.cmd('exec', '-it', '--env=TERM', '@CONTAINER@', 'zsh')

    cli(*args, **kwargs)

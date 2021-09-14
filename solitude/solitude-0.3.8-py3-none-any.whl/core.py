from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    OrderedDict,
    Tuple,
)
from types import ModuleType

import collections
import json
import sys
import tqdm
import re
import logging

from solitude import TOOL_NAME, hookspecs
from solitude.cache import Cache
from solitude.commands import CommandBase, update_jobinfo_for_multiple_commands
import solitude.utils.ssh as ssh
import solitude.plugins.default
import solitude.plugins.csubmit
import solitude.plugins.interactive

from multiprocessing.pool import ThreadPool

import pluggy

from solitude.config import Config
from solitude.slurmjob import SlurmJob

logger = logging.getLogger(TOOL_NAME)


COMMENT_MARKER = "#"
USER_MACRO = "{user}"
SOL_DOCKER_REPO_MACRO = "{sol-docker-repo}"
# these are all aliases for the same repository
SOL_DOCKER_REPO_ALIASES = ["doduo1.umcn.nl", "doduo2.umcn.nl", "doduo.umcn.nl"]
# this is the repository that will be used at core.run
SOL_DOCKER_REPO = "doduo1.umcn.nl"

CommandListType = OrderedDict[str, List[CommandBase]]


def resolve_cmd_files(cmd_files: List[Path]) -> List[str]:
    commands: List[str] = []
    for cmd_file in cmd_files:
        commands = commands + resolve_cmd_file(cmd_file=cmd_file)
    return commands


def resolve_cmd_file(cmd_file: Path) -> List[str]:
    try:
        with open(cmd_file, "r") as f:
            data = f.read()
        # auto-replaces hard-coded SOL_DOCKER_REPO_ALIASES to the SOL_DOCKER_REPO_MACRO
        # this makes started jobs still link to the macro under the hood
        # and facilitates transition to using the macro
        for repo_url in SOL_DOCKER_REPO_ALIASES:
            data = data.replace(repo_url, SOL_DOCKER_REPO_MACRO)
        # extract commands per line
        data_lines = [line.strip() for line in data.splitlines(keepends=False)]
        return [d for d in data_lines if any(d) and d[0] != COMMENT_MARKER]
    except FileNotFoundError:
        logger.error(
            f"ERROR: Could not find command file: {cmd_file}, skipping..."
        )
        return []


def shared_section(
    cmd_files: List[Path], cfg: Config
) -> Tuple[CommandListType, Cache, Optional[Config.SSHConfig]]:
    # load plugins
    plugin_manager = setup_plugins(plugins=cfg.plugins)
    logger.debug(f"Read {len(plugin_manager.get_plugins())} command plugins")
    # load cache file
    cache: Cache = Cache(data_class=SlurmJob, file_name=cfg.cache_path)
    # perform cache auto cleanup (removes expired jobs)
    cache.cleanup()
    # load command files
    cmds_strs = resolve_cmd_files(cmd_files=cmd_files)
    cmds: CommandListType = read_commands(
        commands=cmds_strs, cache=cache, plugin_manager=plugin_manager,
    )
    # retrieve ssh credentials
    return cmds, cache, cfg.ssh


def get_unique_commands(commands: CommandListType) -> List[CommandBase]:
    return [cmd_list[0] for cmd_list in commands.values()]


class ChannelConnectFailedFilter(logging.Filter):
    def filter(self, record):
        return not (
            record.name == "paramiko.transport"
            and re.match(
                r".*ecsh channel \d+ open FAILED: open failed: Connect failed.*",
                record.getMessage(),
            )
        )


class SpecialFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(SpecialFormatter, self).__init__(*args, **kwargs)
        self._main_formatter = logging.Formatter(fmt="%(message)s")
        self._component_formatter = logging.Formatter(
            fmt="[%(name)-10s] %(message)s"
        )

    def format(self, record: logging.LogRecord) -> str:
        if record.name == TOOL_NAME:
            return self._main_formatter.format(record=record)
        else:
            return self._component_formatter.format(record=record)


def log_setup(log_level: int = logging.DEBUG) -> logging.Logger:
    """setup some basic logging"""
    log = logging.getLogger("")
    log.setLevel(log_level)
    fmt = SpecialFormatter()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level)
    ch.setFormatter(fmt)
    log.addHandler(ch)
    logger_pt = logging.getLogger("paramiko.transport")
    logger_pt.setLevel(logging.ERROR)
    logger_pt.addFilter(ChannelConnectFailedFilter())
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("Cache").setLevel(logging.ERROR)
    return logging.getLogger(TOOL_NAME)


def get_attr_from_module(pclass: str) -> Any:
    splitted: List[str] = pclass.rsplit(".", 1)
    mod = __import__(splitted[0], fromlist=[str(splitted[1])])
    return getattr(mod, splitted[1])


def parse_plugins(plugins: List[str]) -> List[ModuleType]:
    results = []
    for plugin_name in plugins:
        if len(plugin_name.strip()) > 0:
            try:
                results.append(get_attr_from_module(plugin_name.strip()))
            except ModuleNotFoundError:
                logger.error(
                    f"!WARNING! Could not find plugin listed in config: {plugin_name}"
                )
    return results


def match_plugin(pm: pluggy.PluginManager, cmd: str) -> ModuleType:
    try:
        idx = pm.hook.matches_command(cmd=cmd).index(True)
    except ValueError:
        raise ValueError(
            f"No plugin found for handling this type of command: {cmd}"
        )
    return pm.hook.matches_command.get_hookimpls()[::-1][idx].plugin


def read_commands(
    commands: List[str], cache: Cache, plugin_manager: pluggy.PluginManager
) -> CommandListType:
    cmds = [
        CommandBase(
            cmd=x, plugin=match_plugin(pm=plugin_manager, cmd=x), cache=cache
        )
        for x in commands
    ]
    cmd_dict: CommandListType = collections.OrderedDict()
    for cmd in cmds:
        hashcode = cmd.hash
        if hashcode in cmd_dict:
            cmd_dict[hashcode].append(cmd)
        else:
            cmd_dict[hashcode] = [cmd]
    return cmd_dict


def execute_commands(
    commands: List[CommandBase],
    map_fn: Callable,
    workers: int,
    show_progress_bar: bool = True,
):
    if workers > 0:
        tpex = ThreadPool(processes=workers)
        list(
            tqdm.tqdm(
                tpex.imap(map_fn, commands),
                total=len(commands),
                desc="Processing cmds ({} threads)".format(workers),
                disable=not show_progress_bar,
            )
        )
    else:
        for cmd in tqdm.tqdm(
            commands,
            desc="Processing cmds (no threads)",
            disable=not show_progress_bar,
        ):
            map_fn(cmd)
    if show_progress_bar:
        logger.info("")


def read_cache(file_name: Path) -> Dict:
    if not file_name.resolve().is_file():
        return {}
    with open(file_name, "r") as f:
        data = json.load(f)
    return data


def extend(
    cmd_files: List[Path], jobids: List[int], workers: int, cfg: Config,
):
    _run_command_on_running_job(
        cmd_files=cmd_files,
        jobids=jobids,
        workers=workers,
        cfg=cfg,
        command="c-extend",
        action_str="EXTENDING",
    )


def stop(
    cmd_files: List[Path], jobids: List[int], workers: int, cfg: Config,
):
    _run_command_on_running_job(
        cmd_files=cmd_files,
        jobids=jobids,
        workers=workers,
        cfg=cfg,
        command="c-stop",
        action_str="STOPPING",
    )


def link(
    cmd_files: List[Path], jobid: int, slurm_jobid: int, cfg: Config
) -> bool:
    ssh_client = get_connected_ssh_client_from_config(cfg, verbose=False)

    commands_dict, cache, _ = shared_section(cmd_files=cmd_files, cfg=cfg)
    commands = get_unique_commands(commands=commands_dict)
    cmd = commands[jobid - 1]
    # link jobid to slurm_jobid
    if SlurmJob.check_if_job_exists(ssh_client=ssh_client, jobid=slurm_jobid):
        job = SlurmJob(ssh_client=ssh_client, jobid=slurm_jobid)
        job.update()
        cache.update(key=cmd.hash, value=job)
        return True
    return False


def get_log(
    cmd_files: List[Path], jobid: int, cfg: Config, active_polling: bool
) -> Optional[str]:
    ssh_client = get_connected_ssh_client_from_config(cfg, verbose=False)
    commands_dict, _, _ = shared_section(cmd_files=cmd_files, cfg=cfg)
    commands = get_unique_commands(commands=commands_dict)
    cmd = commands[jobid - 1]
    cmd.update_job_info(ssh_client=ssh_client)
    if cmd.job_info is not None:
        return cmd.job_info.get_log_text(active_polling=active_polling)
    return None


def get_connected_ssh_client_from_config(
    cfg: Config, verbose: bool = True
) -> ssh.SSHClient:
    ssh_client = ssh.SSHClient(verbose=verbose)
    if cfg.ssh is None:
        logger.error(
            "SSH credentials are not configured in the solitude configuration file."
            "Run `solitude config create` to setup the credentials."
        )
        sys.exit(1)
    ssh_client.connect(*cfg.ssh)
    return ssh_client


def unlink(cmd_files: List[Path], jobid: int, cfg: Config) -> bool:
    commands_dict, cache, _ = shared_section(cmd_files=cmd_files, cfg=cfg)
    commands = get_unique_commands(commands=commands_dict)
    cmd = commands[jobid - 1]
    if cmd.hash in cache:
        cache.delete(key=cmd.hash)
        return True
    return False


def _run_command_on_running_job(
    cmd_files: List[Path],
    jobids: List[int],
    workers: int,
    cfg: Config,
    command: str,
    action_str: str,
):
    ssh_client = get_connected_ssh_client_from_config(cfg=cfg, verbose=False)

    commands_dict, _, credentials = shared_section(
        cmd_files=cmd_files, cfg=cfg
    )
    commands = get_unique_commands(commands=commands_dict)

    # update selected commands only (use workers)
    subcmds = [cmd for idx, cmd in enumerate(commands) if idx + 1 in jobids]

    update_jobinfo_for_multiple_commands(
        commands=subcmds, ssh_client=ssh_client
    )

    ssh_client.verbose = True

    for idx, cmd in zip(jobids, subcmds):
        if cmd.is_running():
            assert cmd.job_info is not None
            logger.info(f"ATTEMPT {action_str} Job: {idx}")
            ssh_client.exec_command(f"./{command} {cmd.job_info.id}")
        else:
            logger.info(f"Job {idx} is no longer running. Skipping...")


def list_jobs(
    cmd_files: List[Path],
    jobids: List[int],
    workers: int,
    cfg: Config,
    selected_only: bool = False,
    show_progress_bar: bool = True,
    show_duplicates: bool = False,
):
    ssh_client = get_connected_ssh_client_from_config(cfg=cfg, verbose=False)

    commands_dict, _, _ = shared_section(cmd_files=cmd_files, cfg=cfg)
    commands = get_unique_commands(commands=commands_dict)

    # update selected commands only (use workers)
    selected_ids = jobids
    if not selected_only:
        jobids = [e for e in range(1, len(commands) + 1)]
    subcmds = [
        cmd
        for idx, cmd in enumerate(commands)
        if (idx + 1 in jobids) or not selected_only
    ]
    mapped_cmds_list = [
        cmd_list
        for idx, cmd_list in enumerate(commands_dict.values())
        if (idx + 1 in jobids) or not selected_only
    ]

    update_jobinfo_for_multiple_commands(
        commands=subcmds, ssh_client=ssh_client
    )

    def _update_cmd(cmd):
        cmd.update_state()
        cmd.update_errors()

    execute_commands(
        subcmds,
        map_fn=_update_cmd,
        workers=workers,
        show_progress_bar=show_progress_bar,
    )
    logger.info("======Commands======")
    logger.info(CommandBase.header_str())
    for idx, cmd, mapped_cmds in zip(jobids, subcmds, mapped_cmds_list):
        logger.info(f'{idx:2d}{"*" if idx in selected_ids else " "} {cmd}')
        if len(mapped_cmds) > 1:
            logger.info(
                f"    (There are {len(mapped_cmds)} lines that map to the above command"
                + (
                    f", run `job list` with the -d flag to list them here)"
                    if not show_duplicates
                    else ")"
                )
            )
            if show_duplicates:
                for lineidx, line in enumerate(mapped_cmds):
                    logger.info(f"    {lineidx + 1:3d} {line.cmd}")


def run(
    cmd_files: List[Path],
    jobids: List[int],
    workers: int,
    user: str,
    priority: str,
    reservation: str,
    duration: int,
    ignore_errors: bool,
    cfg: Config,
    node: Optional[str] = None,
):
    ssh_client = get_connected_ssh_client_from_config(cfg=cfg, verbose=False)

    commands_dict, cache, credentials = shared_section(
        cmd_files=cmd_files, cfg=cfg
    )
    commands = get_unique_commands(commands=commands_dict)

    update_jobinfo_for_multiple_commands(
        commands=commands, ssh_client=ssh_client
    )

    high_priority_job_available = not any(
        [
            c.job_info is not None
            and c.is_running()
            and c.job_info.priority == "high"
            for c in commands
            if c.job_info is not None and c.job_info.user == user
        ]
    )
    if high_priority_job_available:
        logger.info(f"No high priority job running for user {user}!")
    elif priority == "high":
        logger.info(
            f"No high priority job available for user {user}! Switching to low priority..."
        )
        priority = "low"

    # update selected commands only (use workers)
    subcmds = [cmd for idx, cmd in enumerate(commands) if idx + 1 in jobids]

    def _update_cmd(cmd):
        cmd.update_state()
        cmd.update_errors()

    execute_commands(
        subcmds, map_fn=_update_cmd, workers=workers, show_progress_bar=True
    )
    ssh_client.verbose = True

    for idx, cmd in zip(jobids, subcmds):
        logger.info(f"ATTEMPT EXECUTE Job {idx}")
        if cmd.is_running():
            logger.info("Job is already running. skipping...")
            logger.info(str(cmd))
        elif cmd.is_finished():
            logger.info("Job has already finished. skipping...")
            logger.info(str(cmd))
        elif cmd.is_erroneous() and not ignore_errors:
            logger.info(
                "Job has halted with errors. Use --ignore-errors to run anyway. skipping..."
            )
            logger.info(str(cmd))
        else:
            try:
                # set correct priority level in command
                cmdstr = cmd.cmd
                if "c-submit " in cmdstr:
                    cmdstr = format_csubmit_str(
                        cmdstr=cmdstr,
                        duration=duration,
                        priority=priority,
                        reservation=reservation,
                        node=node,
                    )
                cmdstr = cmdstr.replace(USER_MACRO, user)
                cmdstr = cmdstr.replace(SOL_DOCKER_REPO_MACRO, SOL_DOCKER_REPO)

                # attempt schedule command
                result = ssh_client.exec_command(cmdstr)
                if result is not None and ("c-submit " in cmdstr):
                    cmd_output = result[0].strip()
                    if re.match(r"Submitted job \d+", cmd_output):
                        link_id = int(cmd_output.split(" ")[-1])
                        # can have only one high priority job so switch to low priority afterwards
                        cache.update(
                            key=cmd.hash,
                            value=SlurmJob(
                                jobid=link_id, user=user, priority=priority
                            ),
                        )
                        if priority == "high":
                            logger.info(
                                "Assigned a high priority job switching to low priority now"
                            )
                            priority = "low"
                    else:
                        ssh_server_name = (
                            cfg.ssh.server
                            if cfg.ssh is not None
                            else "not-set"
                        )
                        logger.error(
                            f"ERROR - Unexpected c-submit output received: `{cmd_output}`. "
                            f"The command is likely not scheduled. "
                            f"Check if the `c-submit` command works on the configured "
                            f"ssh-server: `{ssh_server_name}` or change the target "
                            f"ssh-server in your configuration."
                        )
            except Exception as e:
                raise e


def format_csubmit_str(
    cmdstr: str,
    priority: str,
    duration: Optional[int],
    reservation: Optional[str],
    node: Optional[str],
) -> str:

    # remove any priority optional flags
    cmdstr = re.sub(r"--priority=[a-zA-Z0-9]*\s", "", cmdstr)
    # add desired priority flag after c-submit command
    cmdstr = re.sub(r"c-submit\s", f"c-submit --priority={priority} ", cmdstr,)
    if node is not None:
        # remove any node optional flags
        cmdstr = re.sub(r"--node=[a-zA-Z0-9]*\s", "", cmdstr)
        cmdstr = re.sub(r"c-submit\s", f"c-submit --node={node} ", cmdstr,)
    if duration is not None:
        cmd_info = re.search(solitude.plugins.csubmit.CSUBMIT_REGEX, cmdstr)
        if cmd_info is None:
            raise ValueError("Unexpected command format found")
        cmd_dict = cmd_info.groupdict()
        cmdstr = re.sub(
            f"\\s+{cmd_dict['user']}\\s+{cmd_dict['ticket']}\\s+{cmd_dict['duration']}\\s+{cmd_dict['image']}",
            f" {cmd_dict['user']} {cmd_dict['ticket']} {duration} {cmd_dict['image']}",
            cmdstr,
        )
    if reservation is not None:
        # remove any reservation optional flags
        cmdstr = re.sub(r"--reservation=[a-zA-Z0-9]*\s", "", cmdstr)
        # add desired reservation flag after c-submit command
        cmdstr = re.sub(
            r"c-submit\s", f"c-submit --reservation={reservation} ", cmdstr,
        )
    return cmdstr


def setup_plugins(
    plugins: List[str], debug: bool = False
) -> pluggy.PluginManager:
    plugin_manager = pluggy.PluginManager(TOOL_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    # Add default fallback plugins
    plugin_manager.register(solitude.plugins.default)
    plugin_manager.register(solitude.plugins.csubmit)
    plugin_manager.register(solitude.plugins.interactive)
    # Load externally packaged plugins
    plugin_manager.load_setuptools_entrypoints(group=TOOL_NAME)
    # Add additional plugins from cfg
    plugins_mods: List[ModuleType] = parse_plugins(plugins=plugins)
    for plugin in reversed(plugins_mods):
        plugin_manager.register(plugin)
    # validate plugins (must strictly implement all plugin methods)
    plugin_manager.check_pending()
    for plugin in plugin_manager.get_plugins():
        validate_plugin(plugin)
    if debug:
        plugin_manager.trace.root.setwriter(print)
        plugin_manager.enable_tracing()
    return plugin_manager


def validate_plugin(plugin: ModuleType):
    required_fns = [
        e for e in dir(solitude.plugins.default) if "__" not in e and "_" in e
    ]
    for fn in required_fns:
        if not hasattr(plugin, fn):
            raise NotImplementedError(
                f"Plugin {plugin} has no hook_implementation for {fn}"
            )

import logging
import socket
import sys
import time
from typing import Optional, Tuple

import paramiko


class SSHClient(object):
    def __init__(self, exit_on_fail: bool = True, verbose: bool = True):
        self.logger = logging.getLogger(type(self).__name__)
        self._exit_on_fail = exit_on_fail
        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connected = False
        self.verbose = verbose

    def connect(self, server: str, username: str, password: str) -> bool:
        try:
            self._ssh.connect(
                hostname=server, username=username, password=password
            )
            self._connected = True
            return True
        except socket.gaierror:
            self.logger.error(
                "Failed to connect to server: {}@{} (socket.gaierror)".format(
                    username, server
                )
            )
            if self._exit_on_fail:
                self.logger.error(
                    "Run `solitude config test` to test the current configuration."
                )
                sys.exit()
        except Exception as e:
            if self._exit_on_fail:
                raise e
            else:
                self.logger.error("Failed with: {}".format(e))
        return False

    def is_connected(self) -> bool:
        return self._connected

    def exec_command(
        self,
        cmd_to_execute: str,
        active_polling: bool = False,
        nbytes: int = 8192,
    ) -> Optional[Tuple[str, str]]:
        if not self.is_connected():
            return None
        if self.verbose:
            self.logger.info("CMD: {}".format(cmd_to_execute))
        try:
            with self._open_channel_session() as chan:
                chan.settimeout(0 if active_polling else None)
                chan.exec_command(cmd_to_execute)
                if active_polling:
                    result_stdout = ""
                    try:
                        done = False
                        while not done:
                            while chan.recv_ready():
                                data = chan.recv(nbytes).decode("utf-8")
                                result_stdout += data
                                print(data, end="")

                            done = chan.exit_status_ready()
                            if not done:
                                time.sleep(1)

                    except KeyboardInterrupt:
                        pass
                    result = (result_stdout, "")
                else:
                    ssh_stdout = chan.makefile("r", nbytes)
                    ssh_stderr = chan.makefile_stderr("r", nbytes)
                    result = (
                        "".join(ssh_stdout.readlines()),
                        "".join(ssh_stderr.readlines()),
                    )
                    if self.verbose:
                        self.logger.info("RESULT: {}".format(result[0]))

                return result
        except Exception as e:
            self.logger.error("Failed with: {}".format(e))
            if self._exit_on_fail:
                sys.exit()
        return None

    def _open_channel_session(
        self, channel_retries: int = 3
    ) -> paramiko.Channel:
        attempts = 1 + max(0, channel_retries)
        transport = self._ssh.get_transport()
        assert transport is not None
        while attempts > 0:
            try:
                return transport.open_session()
            except (
                paramiko.ssh_exception.SSHException,
                paramiko.ssh_exception.ChannelException,
            ) as e:
                unable_to_open_channel_error = (
                    e.code == 2
                    if isinstance(e, paramiko.ssh_exception.ChannelException)
                    else e.args[0] == "Unable to open channel."
                )
                attempts -= 1
                if not unable_to_open_channel_error or attempts == 0:
                    raise e
                time.sleep(1)
        raise RuntimeError("This section should not get reached")

import base64
import json
import logging
import os
import subprocess
import sys
import tempita

DOCKER_CONFIG = os.path.expanduser("~/.docker/config.json")

class EdgeboxOS:
    def __init__(self, mc):
        self.mc = mc

    @property
    def password(self):
        return None

    @password.setter
    def password(self, newpass):
        pass

    @password.deleter
    def password(self):
        pass

    def register_service(self):
        pass

    def _get_docker_auths(self):
        try:
            with open(DOCKER_CONFIG) as f:
                config = json.load(f)
            auths = config["auths"]
        except Exception as e:
            logging.debug("Failed to load docker config: {}".format(e))
            auths = {}
        return auths

    @property
    def docker_logged_in(self):
        # Assume that the user account is stored in the config file
        logging.debug("Checking if user is logged in to docker")
        logged_in = False
        auth = self._get_docker_auths().get(self.mc.docker)
        if auth:
            try:
                auth_decoded = base64.b64decode(auth["auth"]).decode('ascii')
                username = auth_decoded.split(":")[0]
                if username == self.mc.username:
                    logged_in = True
                else:
                    logging.debug("Docker logged in as user: {}".format(username))
            except Exception as e:
                logging.debug("Failed to decode docker auth: {}".format(e))

        return logged_in

class MacOS(EdgeboxOS):
    service_name = "net.mobiledgex.edgeboxagent"
    log_path = os.path.expanduser("~/Library/Logs/MobiledgeX/Edgebox.log")

    @property
    def password(self):
        cmd = ["security", "find-internet-password", "-a", self.mc.username,
               "-s", self.mc.host, "-w"]
        logging.debug("Looking up password in macOS keychain: {}".format(
            " ".join(cmd)))
        p = subprocess.Popen(cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True)
        out, err = p.communicate()
        passwd = out.strip()
        return passwd

    @password.setter
    def password(self, newpass):
        del self.password
        cmd = ["security", "add-internet-password", "-a", self.mc.username,
               "-s", self.mc.host, "-w", self.mc._password]
        logging.debug("Setting password in macOS keychain: {}".format(
            " ".join(cmd)))
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
        out, err = p.communicate()
        if p.returncode != 0:
            logging.warning("Error saving password in keychain: {}".format(err))

    @password.deleter
    def password(self):
        cmd = ["security", "delete-internet-password", "-a", self.mc.username,
               "-s", self.mc.host]
        logging.debug("Deleting password from keychain: {}".format(
            " ".join(cmd)))
        subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _reload_service(self, plist_file):
        logging.debug("Reloading service: {}".format(plist_file))
        subprocess.call(["launchctl", "unload", "-w", plist_file],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.call(["launchctl", "load", "-w", plist_file])

    def register_service(self):
        """Set up a LaunchAgent for restarts after reboot"""
        agent_dir = os.path.expanduser("~/Library/LaunchAgents")
        fname = self.service_name + ".plist"
        plist_file = os.path.join(agent_dir, fname)

        try:
            with open(plist_file) as f:
                plist = f.read()
        except Exception:
            plist = ""

        tmpl = os.path.join(
            os.path.dirname(__file__), "macos_launchagent.plist.tmpl")
        with open(tmpl) as f:
            t = tempita.Template(f.read())
        nplist = (t.substitute(
            service_name=self.service_name,
            log_path=self.log_path,
            edgebox_comm=sys.argv[0]))

        log_dir = os.path.dirname(self.log_path)
        if not os.path.exists(log_dir):
            try:
                os.mkdir(log_dir)
            except Exception as e:
                logging.warning("Error creating log directory: {}".format(
                    log_dir))

        reload_service = False
        if nplist != plist:
            with open(plist_file, "w") as f:
                f.write(nplist)
            reload_service = True
        else:
            p = subprocess.Popen(["launchctl", "list"], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
            out, err = p.communicate()
            for agent in out.splitlines():
                if self.service_name in agent:
                    # Agent already running
                    break
            else:
                reload_service = True

        if reload_service:
            self._reload_service(plist_file)

    @property
    def docker_logged_in(self):
        """Check if docker auth is stored in macOS keychain"""
        auths = self._get_docker_auths()
        if self.mc.docker in auths:
            cmd = ["security", "find-internet-password", "-a", self.mc.username,
                   "-s", self.mc.docker]
            logging.debug("Checking if docker creds are in macOS keychain: {}".format(
                " ".join(cmd)))
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
            out, err = p.communicate()
            logging.debug("Out: {}, Err: {}".format(out, err))
            return p.returncode == 0
        return False

class Linux(EdgeboxOS):
    service_name = "edgebox"
    systemd_dir = os.path.expanduser("~/.config/systemd/user")
    service_file = os.path.join(systemd_dir, service_name + ".service")
    timer_file = os.path.join(systemd_dir, service_name + ".timer")

    @property
    def _password_file(self):
        return os.path.join(self.mc.confdir, ".pass")

    @property
    def password(self):
        pwfile = self._password_file
        logging.debug("Looking for password in {}".format(pwfile))
        try:
            with open(pwfile) as f:
                b64_pw = f.read().strip().encode("ascii")
                return base64.b64decode(b64_pw).decode("utf-8")
        except Exception as e:
            return None

    @password.setter
    def password(self, newpass):
        pwfile = self._password_file
        utf8_pw = newpass.encode("utf-8")
        b64_pw = base64.b64encode(utf8_pw).decode("ascii")
        logging.debug("Writing password to file {}".format(pwfile))
        with open(pwfile, "w") as f:
            f.write(b64_pw)

    @password.deleter
    def password(self):
        pwfile = self._password_file
        logging.debug("Deleting password file {}".format(pwfile))
        if os.path.exists(pwfile):
            os.remove(pwfile)

    def _reload_service(self):
        logging.debug("Reloading service: {}".format(self.service_name))
        for command in [
                ["daemon-reload"],
                ["enable", self.service_name + ".timer"],
                ["start", self.service_name + ".timer"],
        ]:
            subprocess.call(["systemctl", "--user"] + command)

    def register_service(self):
        """Set up a systemd service for restarts after reboot"""
        if not os.path.exists(self.systemd_dir):
            os.makedirs(self.systemd_dir)

        for file in (self.service_file, self.timer_file):
            try:
                with open(file) as f:
                    curr = f.read()
            except Exception:
                curr = ""

            tmpl_name = "linux_" + os.path.basename(file) + ".tmpl"
            tmpl = os.path.join(
                os.path.dirname(__file__), tmpl_name)
            with open(tmpl) as f:
                t = tempita.Template(f.read())
            reqd = (t.substitute(edgebox_comm=sys.argv[0]))

            reload_service = False
            if curr != reqd:
                with open(file, "w") as f:
                    f.write(reqd)
                reload_service = True

        if reload_service:
            self._reload_service()

"""Manage a web host."""

import shutil

import feedparser
import gaea
import pendulum
import semver
import sh
from understory import indieweb, web
from understory.web import tx

app = web.application(
    __name__,
    args={
        "service": r"(digitalocean|dynadot|github)",
        "site": r"[a-z0-9-.]{4,128}",
        "pkg": r"[a-z-]+",
        "app": r"[a-z0-9-:.]{4,128}",
        "developer": r"[a-z]+",
    },
    db=True,
    mounts=(web.framework.data_app, indieweb.indieauth.client.app),
    wrappers=(indieweb.indieauth.client.wrap,),
)


@app.wrap
def contextualize(handler, app):
    """Add a `gaea.Gaea` instance to every request."""
    tx.gaea = gaea.Gaea()
    yield


def get_hostname():
    return sh.hostname("--fqdn")


@app.control(r"")
class Main:
    """Admin interface."""

    def get(self):
        """Render the complete interface as a single page application."""
        self.handle_auth()
        system_hostname = get_hostname()
        system_uptime = sh.uptime()
        config = tx.gaea.get_config()
        sites = []
        for site in tx.gaea.sites_dir.iterdir():
            url = web.uri(site.name)
            try:
                a_record = str(web.dns.resolve(site.name, "A")[0])
            except (web.dns.NoAnswer, web.dns.NXDOMAIN):
                a_record = None
            try:
                ns_records = [str(r) for r in web.dns.resolve(site.name, "NS")]
            except (web.dns.NoAnswer, web.dns.NXDOMAIN):
                ns_records = []
            certified = (site / "domain.crt").exists()
            preloaded = web.in_hsts_preload(site.name)
            sites.append(
                (
                    url.suffix,
                    url.domain,
                    url.subdomain,
                    site,
                    a_record,
                    ns_records,
                    certified,
                    preloaded,
                )
            )
        tokens = config["tokens"]
        dynadot_token = tokens.get("dynadot")
        if dynadot_token:
            dynadot_domains = dict(gaea.dynadot.Client(dynadot_token).list_domain())
        else:
            dynadot_domains = {}
        apps = {}
        for package, applications in web.get_apps().items():
            name = package.metadata["Name"]
            current_version = package.metadata["Version"]
            update_available = None
            versions_url = f"https://pypi.org/rss/project/{name}/releases.xml"
            versions = feedparser.parse(versions_url)["entries"]
            try:
                latest_version = versions[0]["title"]
            except IndexError:
                pass  # TODO fallback to query from GitHub API
            else:
                if semver.compare(current_version, latest_version):
                    update_available = latest_version
            apps[package] = (update_available, applications)
        working = {}
        for project_dir in tx.gaea.working_dir.glob("*/*"):
            project = project_dir.relative_to(tx.gaea.working_dir)
            applications = str(
                sh.Command(f"{tx.gaea.home_dir}/.local/bin/poetry")(
                    "run",
                    "web",
                    "-m",
                    "apps",
                    _cwd=project_dir,
                    _env={},  # NOTE ensures VIRTUAL_ENV is absent
                )
            ).splitlines()
            working[project] = applications
        developers = [f.name for f in tx.gaea.developers_dir.iterdir()]
        return app.view.index(
            system_hostname,
            gaea.get_ip(),
            system_uptime,
            sites,
            dynadot_domains,
            apps,
            working,
            gaea.get_statuses(),
            config,
            developers,
            tx.user,
        )

    def handle_auth(self):
        """Authenticate user using `secret` in query string."""
        secret = web.form(secret=None).secret
        if secret:
            if secret == tx.gaea.get_config()["secret"]:
                web.tx.user.session["signed_in"] = True
                raise web.SeeOther("/")
            raise web.Unauthorized("bad secret")
        elif not web.tx.user.session.get("signed_in", False):
            raise web.Unauthorized("please sign in with your secret")


@app.control(r"tokens/{service}")
class Token:
    """A token for a third-party service."""

    def post(self):
        """Update the locally cached Dynadot API token."""
        token = web.form("token").token
        config = tx.gaea.get_config()
        if token:
            config["tokens"][self.service] = token
        else:
            del config["tokens"][self.service]
        tx.gaea.save_config(config)
        raise web.SeeOther("/")


@app.control(r"sites")
class Websites:
    """Installed sites."""

    def post(self):
        """."""
        site = web.form("site").site
        if not web.uri(site).suffix:
            return "unknown suffix"
        (tx.gaea.sites_dir / site).mkdir()
        raise web.SeeOther("/")


@app.control(r"sites/{site}")
class Website:
    """Installed site."""

    def delete(self):
        """Delete an installed site."""
        shutil.rmtree(tx.gaea.sites_dir / self.site)
        config = tx.gaea.get_config()
        config["websites"].pop(self.site, None)
        tx.gaea.save_config(config)
        raise web.SeeOther("/")


@app.control(r"sites/{site}/dns")
class WebsiteDNS:
    """Site A record."""

    def post(self):
        """Create an A record for given `site`."""
        cli = gaea.digitalocean.Client(tx.gaea.get_config()["tokens"]["digitalocean"])
        site = web.uri(self.site)
        domain_name = f"{site.domain}.{site.suffix}"
        ip = gaea.get_ip()
        if site.subdomain:
            digitalocean_domains = [d["name"] for d in cli.get_domains()["domains"]]
            if self.site in digitalocean_domains:
                cli.create_domain_record(domain_name, site.subdomain, ip)
        else:
            try:
                cli.create_domain(domain_name, gaea.get_ip())
            except gaea.digitalocean.DomainExistsError:
                for record in cli.get_domain_records(domain_name):
                    if record["name"] == "@" and record["type"] == "A":
                        break
                else:
                    raise web.BadRequest("domain exists but couldn't find it")
                cli.update_domain_record(domain_name, record["id"], data=ip)
        raise web.SeeOther("/")


@app.control(r"sites/{site}/certificate")
class WebsiteCertificate:
    """A site's certificate."""

    def get(self):
        """Return a description of the site's certificate."""
        expires = pendulum.from_format(
            str(
                sh.openssl(
                    "x509",
                    "-enddate",
                    "-noout",
                    "-in",
                    tx.gaea.sites_dir / self.site / "domain.crt",
                )
            )
            .partition("=")[2]
            .rstrip(" GMT\n"),
            "MMM  D HH:mm:ss YYYY",
            tz="GMT",
        )
        web.header("Content-Type", "text/html")
        return f"""Expires: {expires}<br>
                   <form action=/sites/{self.site}/certificate method=post>
                     <button>Renew</button>
                   </form>"""

    def post(self):
        """Install or update the site's certificate."""
        site_dir = tx.gaea.sites_dir / self.site
        conf = tx.gaea.nginx_dir / "conf/conf.d" / f"{self.site}.conf"
        if not conf.exists():
            nginx_site_tls_conf = """
            server {{
                listen       80;
                server_name  {site};
            
                location  /.well-known/acme-challenge/  {{
                    alias      /home/gaea/sites/{site}/;
                    try_files  $uri  =404;
                }}
                location  /  {{
                    return  308  https://{site}$request_uri;
                }}
            }}"""

            with conf.open("w") as fp:
                fp.write(nginx_site_tls_conf.format(site=self.site))
            sh.sudo("supervisorctl", "restart", "nginx")
        web.generate_cert(self.site, site_dir, site_dir)
        raise web.SeeOther("/")


@app.control(r"sites/{site}/mount")
class WebsiteMount:
    """Site mount."""

    def post(self):
        """Mount given app at given `site`."""
        app = web.form("app").app
        tx.gaea.mount_site(self.site, app)
        raise web.SeeOther("/")


@app.control(r"apps")
class Applications:
    """Installed applications."""

    def post(self):
        """Install a new application."""
        app = web.form("app").app
        web.enqueue(
            gaea.install_app,
            app,
            str(tx.gaea.home_dir),
            tx.gaea.get_config()["tokens"]["github"],
        )
        return "installing and restarting.."

        # github.com/<username>/<repo_name>

        # XXX owner, _, name = app.partition("/")
        # XXX app = app.removeprefix("https://")
        # XXX if "." in app.partition("/")[0]:
        # XXX     app_url = f"https://{app}"
        # XXX else:
        # XXX     if "/" in app:
        # XXX         owner, _, name = app.partition("/")
        # XXX     else:
        # XXX         owner = name = app
        # XXX     token = tx.gaea.get_config()["tokens"]["github"]
        # XXX     if token:
        # XXX         token += "@"
        # XXX     app_url = (f"git+https://{token}github.com/{owner}/{name}"
        # XXX                f".git#egg={name}")
        # XXX sh.sh("runinenv", "system/env", "pip", "install", "-e",
        # XXX       app_url, _cwd=tx.gaea.home_dir)


@app.control(r"apps/{pkg}")
class Package:
    """Installed application package."""

    def post(self):
        """Upgrade an installed application."""
        web.enqueue(gaea.upgrade_app, self.pkg, str(tx.gaea.home_dir))
        return "upgrading and restarting.."


@app.control(r"apps/{app}")
class Application:
    """Installed application."""

    def post(self):
        """Run an installed application."""
        tx.gaea.run_app(self.app)
        raise web.SeeOther("/")


@app.control(r"developers")
class Developers:
    """Developers."""

    def post(self):
        """Create a developer."""
        form = web.form("system_username", "github_username")
        sh.sudo("adduser", form.system_username, "--disabled-login", "--gecos", "gaea")
        sh.sudo("mkdir", f"/home/{form.system_username}/.ssh")
        sh.ssh_keygen(
            "-o",
            "-a",
            "100",
            "-t",
            "ed25519",
            "-N",
            "",
            "-f",
            f"{tx.gaea.developers_dir}/{form.system_username}",
        )
        sh.sudo("chmod", "700", f"/home/{form.system_username}/.ssh")
        sh.sudo(
            "mv",
            f"{tx.gaea.developers_dir}/{form.system_username}.pub",
            f"/home/{form.system_username}/.ssh/authorized_keys",
        )
        sh.sudo("chmod", "640", f"/home/{form.system_username}/.ssh/authorized_keys")
        sh.sudo(
            "chown",
            f"{form.system_username}:{form.system_username}",
            f"/home/{form.system_username}/.ssh",
            "-R",
        )
        raise web.SeeOther("/")


@app.control(r"developers/{developer}/key")
class DeveloperKey:
    """Developer's key."""

    def get(self):
        with (tx.gaea.developers_dir / self.developer).open() as fp:
            return fp.read()

from dwa import *
import pages
import jobs


def app_workers() -> tuple:
    return (
        jobs.shop.item_info_worker(),
        jobs.shop.reserve_order_worker(),
    )


def get_admin_app() -> tuple:
    return (
        "127.0.0.1",
        pages.shop.get_shop_admin_settings()
    )


def app_settings_template(app_root: str, domain: str, port: int, cookies_expires_day: float) -> dict:
    def csp():
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy
        # https://content-security-policy.com/
        csp = {
            "base-uri": [
                "'self'",
            ],
            "connect-src": [
                "'self'",
            ],
            "default-src": [
                "'none'",
            ],
            "font-src": [
                "'none'",
            ],
            "form-action": [
                "'self'",
            ],
            "frame-ancestors": [
                "'none'",
            ],
            "frame-src": [
                "https://www.google.com",
            ],
            "img-src": [
                "*",
                "data:",
            ],
            "script-src": [
                "'self'",
                "https://cdnjs.cloudflare.com",
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",
            ],
            "worker-src": [
                "'none'",
            ]
        }
        return "; ".join(["{} {}".format(k, " ".join(v)) for k, v in csp.items()])
    def sql_watcher(*args, **kwargs):
        # monitor sql
        # if validated:
        return True
        # else:
        #     raise Exception("something")
    def raise_backend_errors(header, reason):
        # notify via apprise
        pass
    settings = {}
    db = "db/db.db"
    settings["cookie_secret"] = open(os.path.join(app_root, "cookie_secret.txt"), "rb").read()
    settings["port"] = port
    settings["db"] = db
    settings["db_port"] = 39292+0
    settings["writer_port"] = 39292+1
    settings["domain"] = domain
    settings["cookies_expires_day"] = cookies_expires_day
    settings["extra_headers"] = {
        "Referrer-Policy": "no-referrer",
        "Cache-Control": "must-revalidate, max-age=0",
        "Content-Security-Policy": csp(),
    }
    settings["sql_watcher"] = sql_watcher
    settings["raise_backend_errors"] = raise_backend_errors
    settings["admin_contact"] = "<div>Admin contact: test@example.com</div>"
    settings["grr_secret"] = "google recaptcha secret key"
    servers = [
        pages.root.get_root_settings(),
        pages.shop.get_shop_settings(),
        get_admin_app(),
    ]
    settings["servers"] = {k: v for k, v in servers}
    return settings


def app_settings(app_root: str) -> dict:
    return app_settings_template(app_root, "localtest.me", 8888, 0.25)



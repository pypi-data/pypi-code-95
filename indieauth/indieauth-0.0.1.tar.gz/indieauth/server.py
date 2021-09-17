"""A library to facilitate the creation of IndieAuth servers."""

import base64
import hashlib

from understory import sql, web
from understory.web import tx

model = sql.model(
    "IndieAuthServer",
    auths={
        "auth_id": "TEXT",
        "initiated": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "revoked": "DATETIME",
        "code": "TEXT",
        "client_id": "TEXT",
        "client_name": "TEXT",
        "code_challenge": "TEXT",
        "code_challenge_method": "TEXT",
        "redirect_uri": "TEXT",
        "response": "JSON",
        "token": "TEXT",
    },
)

supported_scopes = (
    "create",
    "draft",
    "update",
    "delete",
    "media",
    "profile",
    "email",
)


def initiate_auth(form):
    if form.response_type not in ("code", "id"):  # XXX `id` for backcompat
        raise web.BadRequest('`response_type` must be "code".')
    client, developer = discover_client(form.client_id)
    tx.user.session.update(
        client_id=form.client_id,
        client_name=client["name"],
        redirect_uri=form.redirect_uri,
        state=form.state,
    )
    if "code_challenge" in form and "code_challenge_method" in form:  # FIXME works?
        tx.user.session.update(
            code_challenge=form.code_challenge,
            code_challenge_method=form.code_challenge_method,
        )
    return client, developer


def redeem_authorization_code(form):
    """Verify authenticity and return list of requested scopes."""
    # TODO verify authenticity
    # TODO grant_type=refresh_token
    if form.grant_type not in ("authorization_code", "refresh_token"):
        raise web.Forbidden(f"`grant_type` {form.grant_type} not supported")
    auth = tx.db.select("auths", where="code = ?", vals=[form.code])[0]
    if "code_verifier" in form:
        if not auth["code_challenge"]:
            raise web.BadRequest("`code_verifier` without a `code_challenge`")
        if auth["code_challenge"] != base64.urlsafe_b64encode(
            hashlib.sha256(form.code_verifier.encode("ascii")).digest()
        ).decode().rstrip("="):
            raise web.Forbidden("code mismatch")
    elif auth["code_challenge"]:
        raise web.BadRequest("`code_challenge` without `code_verifier`")

    def complete_redemption(response):
        response["me"] = f"{tx.request.uri.scheme}://{tx.request.uri.netloc}"
        if "profile" in response["scope"]:
            response["profile"] = {
                "name": tx.host.owner["name"][0],
                "url": "TODO",
                "photo": "TODO",
            }
            if "email" in response["scope"]:
                try:
                    response["profile"]["email"] = tx.host.owner["email"][0]
                except KeyError:
                    pass
        tx.db.update("auths", response=response, where="code = ?", vals=[auth["code"]])
        return response

    return auth["response"], complete_redemption


def discover_client(client_id):
    """Return the client name and author if provided."""
    # TODO FIXME unapply_dns was here..
    client = {"name": None, "url": web.uri(client_id).normalized}
    author = None
    if client["url"].startswith("https://addons.mozilla.org"):
        try:
            heading = tx.cache[client_id].dom.select("h1.AddonTitle")[0]
        except IndexError:
            pass
        else:
            client["name"] = heading.text.partition(" by ")[0]
            author_link = heading.select("a")[0]
            author_id = author_link.href.rstrip("/").rpartition("/")[2]
            author = {
                "name": author_link.text,
                "url": f"https://addons.mozilla.org/user/{author_id}",
            }
    else:
        mfs = web.mf.parse(url=client["url"])
        for item in mfs["items"]:
            if "h-app" in item["type"]:
                properties = item["properties"]
                client = {"name": properties["name"][0], "url": properties["url"][0]}
                break
            author = {"name": "NAME", "url": "URL"}  # TODO
    return client, author


class LocalClient:
    def get_clients(self):
        return tx.db.select(
            "auths", order="client_name ASC", what="DISTINCT client_id, client_name"
        )

    def create_auth(self, scopes):
        code = web.nbrandom(32)
        while True:
            try:
                tx.db.insert(
                    "auths",
                    auth_id=web.nbrandom(4),
                    code=code,
                    code_challenge=tx.user.session["code_challenge"],
                    code_challenge_method=tx.user.session["code_challenge_method"],
                    client_id=tx.user.session["client_id"],
                    client_name=tx.user.session["client_name"],
                    redirect_uri=tx.user.session["redirect_uri"],
                    response={"scope": scopes},
                )
            except tx.db.IntegrityError:
                continue
            break
        return code

    def get_auths(self, client_id):
        return tx.db.select(
            "auths",
            where="client_id = ?",
            vals=[f"https://{client_id}"],
            order="redirect_uri, initiated DESC",
        )

    def get_active(self):
        return tx.db.select("auths", where="revoked is null")

    def get_revoked(self):
        return tx.db.select("auths", where="revoked not null")

    def revoke_token(self, token):
        return tx.db.update(
            "auths",
            revoked=web.utcnow(),
            where="json_extract(response, '$.access_token') = ?",
            vals=[token],
        )

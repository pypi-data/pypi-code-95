"""An IndieAuth server for the Understory framework."""

from __future__ import annotations

from indieauth import server
from understory import web
from understory.web import tx

app = web.application(
    __name__,
    prefix="auth",
    args={
        "client_id": r"[\w/.]+",
    },
    model=server.model,
)


def wrap(handler, mainapp):
    """Ensure server links are in head of root document."""
    tx.auth = server.LocalClient()
    yield
    if tx.request.uri.path == "":
        base = f"{tx.origin}/auth"
        web.add_rel_links(
            authorization_endpoint=f"{base}",
            token_endpoint=f"{base}/tokens",
            ticket_endpoint=f"{base}/tickets",
        )


@app.control(r"")
class AuthorizationEndpoint:
    """IndieAuth server `authorization endpoint`."""

    def get(self):
        """Return a consent screen for a third-party site sign-in."""
        if not tx.user.is_owner:
            raise web.OK(app.view.root(tx.host.owner, tx.auth.get_clients()))
        try:
            form = web.form(
                "response_type",
                "client_id",
                "redirect_uri",
                "state",
                scope=[],
            )
        except web.BadRequest:
            return app.view.authorizations(
                tx.auth.get_clients(), tx.auth.get_active(), tx.auth.get_revoked()
            )
        client, developer = server.initiate_auth(form)
        return app.view.signin(client, developer, form.scope, server.supported_scopes)

    def post(self):
        """Handle "Profile URL" flow response."""
        form = web.form(
            "code", "client_id", "redirect_uri", grant_type="authorization_code"
        )
        response, complete = server.redeem_authorization_code(form)
        web.header("Content-Type", "application/json")
        return complete(response)


@app.control(r"consent")
class AuthorizationConsent:
    """The authorization consent screen."""

    def post(self):
        """Handle consent screen action."""
        form = web.form("action", scopes=[])
        redirect_uri = web.uri(tx.user.session["redirect_uri"])
        if form.action == "cancel":
            raise web.Found(redirect_uri)
        redirect_uri["code"] = tx.auth.create_auth(form.scopes)
        redirect_uri["state"] = tx.user.session["state"]
        raise web.Found(redirect_uri)


@app.control(r"tokens")
class TokenEndpoint:
    """A token endpoint."""

    def get(self):
        return "token endpoint: show tokens to owner; otherwise form to submit a code"

    def post(self):
        """Create or revoke an access token."""
        # TODO token introspection
        # TODO token verification
        try:
            form = web.form(
                "code", "client_id", "redirect_uri", grant_type="authorization_code"
            )
        except web.BadRequest:
            pass
        else:
            response, complete = server.redeem_authorization_code(form)
            if not response["scope"]:
                raise web.BadRequest("Access Token request requires a scope")
            response.update(
                token_type="Bearer",
                access_token=f"secret-token:{web.nbrandom(12)}",
            )
            web.header("Content-Type", "application/json")
            return complete(response)
        form = web.form("action", "token")
        if form.action == "revoke":
            tx.auth.revoke_token(form.token)
            raise web.OK("")


@app.control(r"tickets")
class TicketEndpoint:
    """A ticket endpoint."""

    def get(self):
        return "ticket endpoint: if owner, show tickets; else form to submit a ticket"


@app.control(r"clients")
class Clients:
    """Authorized clients."""

    def get(self):
        return app.view.clients(tx.auth.get_clients())


@app.control(r"clients/{client_id}")
class Client(web.Resource):
    """An authorized client."""

    def get(self):
        return app.view.client(tx.auth.get_auths(self.client_id))


# @app.migrate(1)
# def change_name(db):
#     db.rename_column("auths", "revoked", "revoced")

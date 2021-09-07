import pprint
from flask import Blueprint, render_template, make_response, current_app, request, redirect, session, url_for, send_from_directory, jsonify, abort, g

# return debugger(request, session, "Install page", permission_url)
# return debugger(request, session, pprint.pformat(shop), redirect_url)
# return debugger(request, session, "Main page", redirect_url)


def debugger(request, session, message, link):
    return render_template("shopify_bp/debugger.html", request=pprint.pformat(request.__dict__, 1, 2400), session=pprint.pformat(dict(session)), message=message, link=link)

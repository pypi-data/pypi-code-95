# -*- coding: utf-8 -*-
"""
EmberFactory / site navigation: manages the pages that are not directly related to ember production

Written as a flask Blueprint; if revising the app structure is desired, consider reading
https://stackoverflow.com/questions/24420857/what-are-flask-blueprints-exactly

Copyright (C) 2020  philippe.marbaix@uclouvain.be
"""

from flask import Blueprint
from flask import render_template
from flask import url_for, redirect
from flask import current_app
from flask import request
from flask import send_from_directory
from flask import session
import os
from markdown import markdown
from emberweb import helpers as webhlp

bp = Blueprint("sitenav", __name__)


@bp.route("/index")
def index():
    if "reset" in request.args:
        session["result-msg"] = None

    # If a result is available, move to the result page
    if "result-msg" in session and session["result-msg"] is not None and os.path.isfile(session["pdfpathname"]):
        return redirect(url_for('control.result'))

    # If there is no result available, show the start page
    else:
        settings = {'checked_rgb': '', 'checked_cmyk': '', 'checked_standard': ''}
        if current_app.config['UI_PREFERRED_COLOR_SPACE'] == 'CMYK':
            settings['checked_cmyk'] = 'checked'
        elif current_app.config['UI_PREFERRED_COLOR_SPACE'] == 'RGB':
            settings['checked_rgb'] = 'checked'
        else:
            settings['checked_standard'] = 'checked'  # Default and fallback if config id mistyped
        return render_template("emberweb/start.html", settings=settings)


# Enable downloading examples:
@bp.route('/doc/examples/<path:filename>', methods=['GET', 'POST'])
def examples_fil(filename):
    examples_dir = os.path.join(current_app.root_path, "doc/examples/")
    return send_from_directory(examples_dir, filename)


# Load the 'doc' pages (examples and documentation about parameters etc.)
# Doc pages are written in markdown and included in the doc/ folder.
@bp.route('/doc/<subpage>', methods=['GET', 'POST'])
@bp.route('/doc/', methods=['GET', 'POST'])
def doc(subpage='tutorial'):
    doc_page = os.path.join(current_app.root_path, 'doc/'+subpage+'.md')
    try:
        with open(doc_page, "r", encoding="utf-8") as input_file:
            content = input_file.read()
    except FileNotFoundError:
        return render_template("emberweb/error.html", message={"error": "Could not handle request"})

    # Add support for a specific-type of file inclusion
    content = webhlp.mdcombine(content, current_app.root_path)
    # Process markdown
    content = markdown(content, extensions=['tables'])
    # Add support for colspan when empty cells are found
    content = webhlp.colspan(content)
    # Add code to transform links to buttons when at the beginning of a paragraph
    txbutton = 'class="btn btn-right" > <svg class="btn-icon" aria-hidden="true">\
        <use href=' + url_for('static', filename='icons.svg') + '#download></use></svg>'
    txmarker = '<p><a href'
    thesplit = content.split(txmarker)
    content = thesplit[0]
    for txfrag in thesplit[1:]:
        content += txmarker + txfrag.replace('>', txbutton, 1)

    return render_template("emberweb/doc.html", content=content, pagename=subpage)


# Load the 'More information' page
@bp.route('/more')
def more():
    return render_template("emberweb/more.html")

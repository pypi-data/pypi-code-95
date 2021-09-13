# -*- coding: utf-8 -*-
"""
EmberFactory / control: links the web UI to the drawing code

Written as a flask Blueprint; if revising the app structure is desired, consider reading
https://stackoverflow.com/questions/24420857/what-are-flask-blueprints-exactly

Copyright (C) 2020  philippe.marbaix@uclouvain.be
"""

from flask import Blueprint
from flask import render_template
from flask import request, url_for, redirect
from flask import current_app, session
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
import sys
import uuid
import datetime
from embermaker import helpers as hlp
from embermaker import makember as mke
import tempfile
import logging
from shutil import copyfile

bp = Blueprint("control", __name__)

# Process the received data (=> action when data is submitted from the start page)
@bp.route('/process', methods=['GET', 'POST'])
def process():
    # Avoid failure if this page is visited without providing data
    if request.method == 'GET':
        return redirect(url_for('sitenav.index'))

    # Default message to be returned within the template
    message = {"error": "", "warning": "", "log": [], "uncaught-err": False}
    session['result-msg'] = None
    session['dirname'] = None

    # File upload and embermaker run
    # ------------------------------
    hlp.startlog()
    try:
        # Get filename and check file
        fileitem = request.files['file']
        if not fileitem:
            message["error"] = "No file provided or bad file."
        else:
            fnamesplit = os.path.splitext(os.path.basename(fileitem.filename))
            # Reject file if the extension does not suggest an Excel file
            # (wile devils can masquerade as angels, this protects against potential evils who look like evils)
            if fnamesplit[1] == '.xls':
                message["error"] = "The EmberFactory cannot process .xls files, please convert it to .xlsx."
            elif fnamesplit[1] != '.xlsx':
                message["error"] = "Unexpected file extension."
        if message["error"]:
            session["result-msg"] = None
            return render_template("emberweb/error.html", message=message)

        # Create a temporary folder to store files related to this request
        tmpdir = tempfile.TemporaryDirectory()
        # Create subdirectories for in and out so that we will never read from a folder to which the user can 'write'
        indirname = os.path.join(tmpdir.name, 'in')
        outdirname = os.path.join(tmpdir.name, 'out')
        os.makedirs(indirname)
        os.makedirs(outdirname)

        # Schedule timed deletion of the temporary folder
        current_app.scheduler.add_job(tmpdir.cleanup, 'date',
                                      run_date=(datetime.datetime.now() + datetime.timedelta(hours = 2)))
        # Set pathname + upload file
        infile = os.path.join(indirname, secure_filename(os.path.basename(fileitem.filename)))
        fileitem.save(infile)

        # If user accepted to leave file
        if not request.form.get('delfile'):
            fnamesplit = os.path.splitext(os.path.basename(fileitem.filename))
            fname = secure_filename(str(uuid.uuid1()) + fnamesplit[1]) # replaces name by random unique name
            keptfile = os.path.join(current_app.instance_path, 'in/', fname)
            copyfile(infile,keptfile)

        # Execution of makember
        makeres = mke.makember(infile=infile, prefcsys=request.form['csys'])

        # An output file was generated (success!)
        if 'error' not in makeres:
            outfile = makeres['outfile']
            # Provide a url for the download, but without the extension, because we will have several ones:
            # (for details, see the download function below and the result.html template)
            begname = os.path.splitext(os.path.basename(outfile))[0]
            message["begname"] = begname  # inserts url for download
            # Report logged messages
            message["log"] = hlp.getlog("full")
            warnings = hlp.getlog("warning")
            if len(warnings) > 0:
                message["warning"] = warnings
            critical = hlp.getlog("critical")
            if len(critical) > 0:
                message["error"] = critical
            message['img-width'] = makeres['width']
            session['dirname'] = outdirname
            session['result-msg'] = message
            session['pdfpathname'] = outfile
            return redirect(url_for('control.result'))

        # No file was generated: a fatal error occurred:
        else:
            message["error"] = "Execution generated the following message, then failed: " + str(makeres['error'])
            session["result-msg"] = None  # This might move to an error function to avoid duplication?
            return render_template("emberweb/error.html", message=message)

    # An error occurred, and we did not handle it in any way:
    except Exception as exc:
        message["error"] = "An error for which there is no handling has occurred. " \
                           "We apologize. The details provided below may help to understand the problem." \
                           "It might relate to an issue in your input file. We are interested in " \
                           "receiving this information to improve the Ember Factory (see contact at the bottom)."
        exc_tb = sys.exc_info()[2]
        errtrace = ""
        errtype = ""
        while exc_tb.tb_next is not None:
            if errtrace != "":
                errtrace += ">> "
            exc_tb = exc_tb.tb_next
            try:
                finame = exc_tb.tb_frame.f_globals['__name__']
                lineno = str(exc_tb.tb_frame.f_lineno)
                errtype = type(exc).__name__
                errtrace += "[" + finame + ":" + lineno + "] "
            except KeyError:
                pass
        errtrace += errtype + " (" + str(exc) + ")"
        hlp.addlogfail(errtrace)
        message["log"] = hlp.getlog("full")
        message["uncaught-err"] = True
        session["result-msg"] = None  # This might move to an error function to avoid duplication?
        return render_template("emberweb/error.html", message=message)

# This function shows the results of processing the submitted data.
@bp.route('/result', methods=['GET', 'POST'])
def result():
    # If no result is available, go back to the start page (msg and file may disappear separately and are both needed)
    if "result-msg" not in session or session["result-msg"] is None or not os.path.isfile(session["pdfpathname"]):
        return redirect(url_for('sitenav.index'))

    return render_template("emberweb/result.html", message=session["result-msg"])

# Raster image filenames and production recipes (used by the download method below):
# The dict contains: file-suffix: (img-type, width, dpi, quality)
# This mechanism provides flexibility; settings might be improved by learning about pdf2image and Poppler
imrecipes = {
    '-sc.png': ('png', 750, 200, None),
    '-re.png': ('png', 1500, 200, None),
    '-mr.png': ('png', None, 200, None),
    '-mr.jpg': ('jpeg', None, 300, {"quality": 70, "optimize": True, "progressive": False})
}

# Enable downloading the resulting files:
@bp.route('/out/<filename>', methods=['GET', 'POST'])
def download(filename):
    """
    If file name is available in the filesystem, return the file; otherwise,
    try to get it from converting the PDF on the basis on indications in the filename's suffix (last 7 char),
    using data from dict 'imrecipes'; return converted file when successful.
    :param filename:
    :return:
    """
    if 'pdfpathname' not in session or not os.path.isfile(session['pdfpathname']):
        logging.warning("Bad file request")
        return render_template("emberweb/error.html", message={"error": "No resulting diagram available. "
                               "Please note that files are deleted after 2 hours."})

    filepath = os.path.join(session['dirname'], filename)
    if not os.path.isfile(filepath):
        # The file is not available yet; check imrecipes to see if we can generate it from the PDF:
        if len(filename) < 8 or filename[-7:] not in imrecipes:
            return render_template("emberweb/error.html", message={"error":"Could not handle request"})
        recipe = imrecipes[filename[-7:]]
        # Generate the image file from the PDF according to information from the recipe:
        pdfpath = filepath[:-7]+".pdf"
        outpath = hlp.rasterize(pdfpath, filename, *recipe)
        if not outpath:
            return render_template("emberweb/error.html", message={"error":"File conversion failed"})

    response = send_from_directory(session['dirname'], filename)
    if not filename.endswith('-sc.png'): # Except for screen preview
        response.headers['Content-Disposition'] = 'attachment'
    return response

from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY
import os
from plone import api
from plone.app.textfield.value import RichTextValue
from csv import reader
from six.moves import cStringIO
import logging


def import_content(context):
    pages_dir = os.path.join(
        os.path.dirname(__file__), 'pages', )
    # list_contents = [f for f in os.listdir(pages_dir)]

    """Read file listing content to import"""
    objects = _read_file('.objects', pages_dir)
    if objects is None:
        logging.getLogger(__name__).info(
            "Could not find .objects file in %s" % pages_dir)
        return

    dialect = 'excel'
    stream = cStringIO(objects)

    rowiter = reader(stream, dialect)
    rows = [i for i in rowiter if i]

    portal = api.portal.get()

    # create training parent folder
    if 'mosaic-user-training-guide' in portal:
        parent_folder = portal['mosaic-user-training-guide']
    else:
        parent_folder = api.content.create(
            type='Folder',
            id='mosaic-user-training-guide',
            title='Mosaic User Training Guide',
            container=portal,
        )
        # enable next/previous navigation on folder
        parent_folder.nextPreviousEnabled = True

        # block right parent portlets on folder
        manager = getUtility(IPortletManager, name=u"plone.rightcolumn")
        assignable = getMultiAdapter((parent_folder, manager),
                                     ILocalPortletAssignmentManager)
        for category in CONTEXT_CATEGORY, GROUP_CATEGORY:
            assignable.setBlacklistStatus(category, True)

    for id, title, type in rows:
        try:
            html_text = _load_html(id, pages_dir)
        except FileNotFoundError:
            continue

        if id in parent_folder:
            continue
        new_content = api.content.create(  # noqa: F841
            type=type,
            title=title,
            id=id,
            container=parent_folder,
            text=html_text,
        )

    if 'introduction' in parent_folder:
        parent_folder.setDefaultPage('introduction')


def _read_file(filename, path):
    file_contents = None
    file_path = os.path.join(path, filename, )
    if file_path is not None:
        try:
            with open(file_path, 'r') as file_opened:
                file_contents = file_opened.read()
        except FileNotFoundError:
            pass
    return file_contents


def _load_html(file_id, file_dir):
    html_file = os.path.join(file_dir, '{0}.html'.format(file_id),)
    with open(html_file, 'r') as html_opened:
        file_text = html_opened.read()
    return RichTextValue(
        raw=file_text, mimeType='text/html',
        outputMimeType='text/html', encoding='utf-8',
    )

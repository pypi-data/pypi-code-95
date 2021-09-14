#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_thesaurus.zmi.tests module

A test module for several PyAMS_thesaurus widgets
"""

from persistent import Persistent
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces.base import MANAGE_SYSTEM_PERMISSION
from pyams_site.interfaces import ISiteRoot
from pyams_thesaurus.interfaces.thesaurus import IThesaurus
from pyams_thesaurus.schema import ThesaurusTermsListField
from pyams_thesaurus.zmi.widget import ThesaurusTermsTreeFieldWidget
from pyams_utils.adapter import adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config
from pyams_utils.registry import query_utility
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IPropertiesMenu
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


class IThesaurusTest(Interface):
    """Thesaurus test interface"""

    field1 = ThesaurusTermsListField(title=_("Thesaurus terms"),
                                     required=False)


@factory_config(provided=IThesaurusTest)
class ThesaurusTest(Persistent):
    """Thesaurus test persistent class"""

    field1 = FieldProperty(IThesaurusTest['field1'])


PYAMS_THESAURUS_TEST_KEY = 'pyams_thesaurus.test'


@adapter_config(required=ISiteRoot,
                provides=IThesaurusTest)
def site_root_thesaurus_test_adapter(context):
    """Site root thesaurus test adapter"""
    return get_annotation_adapter(context, PYAMS_THESAURUS_TEST_KEY, IThesaurusTest)


@viewlet_config(name='thesaurus-test.menu',
                context=ISiteRoot, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=900,
                permission=MANAGE_SYSTEM_PERMISSION)
class ThesaurusTestMenu(NavigationMenuItem):
    """Thesaurus test menu"""

    label = _("Test thesaurus widgets")
    href = '#thesaurus-test.html'


@ajax_form_config(name='thesaurus-test.html',
                  context=ISiteRoot, layer=IPyAMSLayer,
                  permission=MANAGE_SYSTEM_PERMISSION)
class ThesaurusTestForm(AdminEditForm):
    """Thesaurus test form"""

    title = _("Thesaurus test form")
    legend = _("Thesaurus widget test")

    fields = Fields(IThesaurusTest)
    fields['field1'].widget_factory = ThesaurusTermsTreeFieldWidget

    label_css_class = 'control-label col-md-2'
    input_css_class = 'col-md-10'

    def get_content(self):
        """Form content getter"""
        return IThesaurusTest(self.context)

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        field1 = self.widgets.get('field1')
        if field1 is not None:
            field1.thesaurus_name = 'Tags'


@adapter_config(name='field1',
                required=(IThesaurusTest, IAdminLayer, ThesaurusTestForm),
                provides=IThesaurus)
def thesaurus_test_thesaurus_adapter(context, request, view):  # pylint: disable=unused-argument
    """Thesaurus test thesaurus adapter"""
    return query_utility(IThesaurus, name='Tags')

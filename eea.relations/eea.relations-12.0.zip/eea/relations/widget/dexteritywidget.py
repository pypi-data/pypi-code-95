from plone.app.relationfield.behavior import IRelatedItems
from plone.app.z3cform.interfaces import IPloneFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer, Interface
from z3c.form.converter import BaseDataConverter
from z3c.relationfield.interfaces import IRelationList
from plone.app.z3cform.wysiwyg.widget import WysiwygWidget
from plone.uuid.interfaces import IUUID
from zope.interface import implements
from plone.app.uuid.utils import uuidToObject


@adapter(getSpecification(IRelatedItems['relatedItems']), IPloneFormLayer)
@implementer(IFieldWidget)
def RelatedItemsFieldWidget(field, request):
    widget = FieldWidget(field, CustomizedRelatedItemsFieldWidget(field, request))
    return widget


class IRelatedItemsWidget(Interface):
    """ Marker interface
    """


class RelatedItemsWidget(WysiwygWidget):
    """
    """
    implements(IRelatedItemsWidget)

    def enter_pdb(self):
        import pdb; pdb.set_trace()
        return 'x'

    @property
    def fieldname(self):
        return self.field.__name__


@implementer(IFieldWidget)
def CustomizedRelatedItemsFieldWidget(field, request):
    return FieldWidget(field, RelatedItemsWidget(request))


@adapter(IRelationList, IRelatedItemsWidget)
class RelatedItemsFieldDataConverter(BaseDataConverter):
    """A data converter using the field's ``fromUnicode()`` method."""

    type = None
    errorMessage = None
    _strip_value = False

    def toWidgetValue(self, value):
        """Convert the internal stored value into something that a
        z3c.form widget understands.
        :param value: [required] The internally stored value
        :returns: A list with UUIDs
        """
        if value in [None, []]:
            return []
    
        uuids = [IUUID(val, None) for val in value]
        return uuids

    def toFieldValue(self, value):
        """Pass the value extracted from the widget to the internal
        structure. In this case, the value expected is already formatted.
        :param value: [required] The data extracted from the widget
        :type value: list
        :returns: The value to be stored in the tile
        """
        if isinstance(value, basestring):
            value = [value, ]

        if not len(value) or not isinstance(value, list):
            return self.field.missing_value

        related = [uuidToObject(uid) for uid in value]
        return related
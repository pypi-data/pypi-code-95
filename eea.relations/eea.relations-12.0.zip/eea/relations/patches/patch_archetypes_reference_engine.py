from Acquisition import aq_base
from Products.Archetypes.exceptions import ReferenceException
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName

def patched_uidFor(self, obj):
    # We should really check for the interface but I have an idea
    # about simple annotated objects I want to play out
    if not isinstance(obj, basestring):
        uobject = aq_base(obj)
        if not self.isReferenceable(uobject):
            raise ReferenceException, "%r not referenceable" % uobject

        uuid = IUUID(uobject, None)
        if uuid is None:
            uuid = self._getUUIDFor(uobject)

    else:
        uuid = obj
        obj = None
        # and we look up the object
        uid_catalog = getToolByName(self, 'uid_catalog')
        brains = uid_catalog(dict(UID=uuid))
        # 134485 look for object from portal_catalog
        # for situations where we point to a dexterity content type
        if not brains:
            portal_catalog = getToolByName(self, 'portal_catalog')
            brains = portal_catalog(UID=uuid)
        for brain in brains:
            res = brain.getObject()
            if res is not None:
                obj = res
    return uuid, obj

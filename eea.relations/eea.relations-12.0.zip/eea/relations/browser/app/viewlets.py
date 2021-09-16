""" eea.versions viewlets
"""
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter



class RelationsStatusViewlet(ViewletBase):
    """ Viewlet to show status of versioning on any content type
    """

    def available(self):
        """ Method that enables the viewlet only if we are on a
            view template
        """
        plone = getMultiAdapter((self.context, self.request),
                                name=u'plone_context_state')

        plone_state = getMultiAdapter((self.context, self.request),
                                name=u'plone_portal_state')
        return plone.is_view_template() and not plone_state.anonymous()

    def no_relations_entered(self):
        """
        """
        macro_view = self.context.restrictedTraverse('eea.relations.macro')
        return macro_view.no_relations_entered()


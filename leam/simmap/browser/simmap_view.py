from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from leam.simmap import simmapMessageFactory as _


class ISimMapView(Interface):
    """SimMap view interace"""

    contents = schema.Object(Inteface)


class SimMapView(BrowserView):
    """SimMap browser view"""
    implements(ISimMapView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def __call__(self):
        """
        Render the content item
        """
        pass




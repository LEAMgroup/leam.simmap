from zope.interface import implements, Interface
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from leam.simmap import simmapMessageFactory as _
from leam.simmap.interfaces import ISimMapSettings


class ISimMapView(Interface):
    """SimMap view interace"""


class SimMapView(BrowserView):
    """SimMap browser view"""
    implements(ISimMapView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISimMapSettings)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def mapserver(self):
        return self.settings.mapserver


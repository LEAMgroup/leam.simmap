from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from plone.app.layout.globals.interfaces import IViewView

from leam.simmap import simmapMessageFactory as _


class IstandardView(Interface):
    """
    standard view interface
    """

    def test():
        """ test method"""

    def data():
        """ access to the real data """

class standardView(BrowserView):
    """
    standard browser view
    """
    implements(IstandardView, IViewView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')
        dummy2 = self.context.title
        title = self.context.title
        image = self.context.zoom

        return {'dummy': dummy, 'dummy2': dummy2, 'title': title, 'image': image}


    def data(self):
        """ real data method """
        title = self.context.title
        description = self.context.description
        latlong = self.context.latlong
        zoom = self.context.zoom
        size = (8 + 3) * 5
        image = str(self.context.simImage)

        return {'title': title, 'description': description, 'latlong': latlong, 'zoom': zoom, 'size': size, 'image': image}



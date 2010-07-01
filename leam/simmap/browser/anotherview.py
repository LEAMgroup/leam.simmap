from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from leam.simmap import simmapMessageFactory as _


class IanotherView(Interface):
    """
    another view interface
    """

    def test():
        """ test method"""

    def data():
        """ access to the real data """


class anotherView(BrowserView):
    """
    another browser view
    """
    implements(IanotherView)

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
        image = getMapPath();

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

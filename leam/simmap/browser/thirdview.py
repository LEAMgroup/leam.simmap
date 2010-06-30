from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from leam.simmap import simmapMessageFactory as _


class IthirdView(Interface):
    """
    third view interface
    """

    def test():
        """ test method"""


class thirdView(BrowserView):
    """
    third browser view
    """
    implements(IthirdView)

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

        return {'dummy': dummy}

from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class SimMapViewlet(ViewletBase):

    template = ViewPageTemplateFile("simmap_viewlet.pt")

    def render(self):
        return self.template()

class SimMapHtmlHeadViewlet(ViewletBase):

    template = ViewPageTemplateFile("simmap_htmlhead.pt")

    def render(self):
        return self.template()

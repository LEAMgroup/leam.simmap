from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from leam.simmap import simmapMessageFactory as _

class Isimmap(Interface):
    """SimMap version 2"""
    
    # -*- schema definition goes here -*-
    location = schema.TextLine(
        title=_(u"Grass location (optional)"), 
        required=False,
        description=_(u"Specify to upload to Grass, otherwise leave blank"),
    )

    simImage = schema.Bytes(
        title=_(u"Simulation image file"), 
        required=True,
        description=_(u"Field description"),
    )

    mapFile = schema.Bytes(
        title=_(u"Map file"), 
        required=False,
        description=_(u"Field description"),
    )

    Transparency = schema.Float(
        title=_(u"Transparency"), 
        required=False,
        description=_(u"Please enter the transparency for the overlays (0.0 = fully transparent; 1.0 = fully opaque)"),
    )

    latlong = schema.TextLine(
        title=_(u"Latitude Longitude"), 
        required=True,
        description=_(u"Please enter the latitude and longintude in decimal degrees separated by a space: 40.1234 -120.1234"),
    )

    zoom = schema.Int(
        title=_(u"Zoom level"), 
        required=True,
        description=_(u"Please set the GMap zoom level"),
    )


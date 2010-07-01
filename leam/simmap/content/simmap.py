"""Definition of the simmap content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from leam.simmap import simmapMessageFactory as _
from leam.simmap.interfaces import Isimmap
from leam.simmap.config import PROJECTNAME


simmapSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'grass_location',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Grass location (optional)"),
            description=_(u"Specify to upload to Grass, otherwise leave blank"),
        ),
    ),


    atapi.FileField(
        'simImage',
        storage=atapi.AnnotationStorage(),
        widget=atapi.FileWidget(
            label=_(u"Simulation image file"),
            description=_(u""),
        ),
        required=True,
        validators=('isNonEmptyFile'),
    ),


    atapi.FileField(
        'mapFile',
        storage=atapi.AnnotationStorage(),
        widget=atapi.FileWidget(
            label=_(u"Map file"),
            description=_(u""),
        ),
        validators=('isNonEmptyFile'),
    ),


    atapi.FloatField(
        'Transparency',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Transparency"),
            description=_(u"Please enter the transparency for the overlays (0.0 = fully transparent, 1.0 = fully opaque)"),
        ),
        default=_(u"0.7"),
        validators=('isDecimal'),
    ),


    atapi.StringField(
        'latlong',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Latitude Longitude"),
            description=_(u"Please enter the latitude and longintude in decimal degrees separated by a space: 40.1234 -120.1234"),
        ),
        required=True,
    ),


    atapi.IntegerField(
        'zoom',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Zoom level"),
            description=_(u"Please set the GMap zoom level"),
        ),
        required=True,
        validators=('isInt'),
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

simmapSchema['title'].storage = atapi.AnnotationStorage()
simmapSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(simmapSchema, moveDiscussion=False)

class simmap(base.ATCTContent):
    """SimMap version 2"""
    implements(Isimmap)

    meta_type = "simmap"
    schema = simmapSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    location = atapi.ATFieldProperty('location')

    simImage = atapi.ATFieldProperty('simImage')

    mapFile = atapi.ATFieldProperty('mapFile')

    Transparency = atapi.ATFieldProperty('Transparency')

    latlong = atapi.ATFieldProperty('latlong')

    zoom = atapi.ATFieldProperty('zoom')




atapi.registerType(simmap, PROJECTNAME)

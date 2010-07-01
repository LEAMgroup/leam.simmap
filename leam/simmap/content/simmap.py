"""Definition of the simmap content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from leam.simmap import simmapMessageFactory as _
from leam.simmap.interfaces import Isimmap
from leam.simmap.config import PROJECTNAME


# old_simmap imports
from persistent import Persistent
#from Products.Archetypes.atapi import *
#from Products.Archetypes.interfaces import *
#from Products.CMFCore import permissions
try:
    from iw.fss.FileSystemStorage import FileSystemStorage
except ImportError:
    from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage
from Products.validation import V_REQUIRED
from AccessControl import ClassSecurityInfo
#from Products.SimMap.config import PROJECTNAME, PROTOCOLS
from zope.component import adapter
import os
import IMGconvert


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



#old_simmap methods
	# This no longer gets used
	# Now, all files are processed/created upon first run
	# DEPRECATED: all functions now done on first run by getMapPath()
	def postCreateScript(self):
	        # image=self.getSimImage().getData()
		# mapFile=self.getMapFile().getData()
		image = str(self.getFilename('simImage'))
		mapFile = str(self.getFilename('mapFile'))
		writeDir = self.getPhysicalPath()
                location=self.getLocation()
                if self.getLatlong() == '':
	            self.latlong = IMGconvert.createFiles(image, mapFile, writeDir, self.id, location)
                else:
                    IMGconvert.createFiles(image, mapFile, writeDir, location)

	# Script that is run after an edit
	# Needs to update map files since edit will change them
	def postEditScript(self):
		mapFile = str(self.getFilename('mapFile'))
		writeDir = self.getPhysicalPath()
		customMapFile = IMGconvert.makePath('leam.'+mapFile, writeDir) 
		image = str(self.getFilename('simImage'))
		location=self.getLocation()
		if self.getLatlong() == '':
	           self.latlong = IMGconvert.createFiles(image, mapFile, writeDir, location)
                else:
                   IMGconvert.createFiles(image, mapFile, writeDir, location)
		    
		return customMapFile


	# script to run when an object is deleted through plone
	def manage_beforeDelete(self, item, container):
		BaseContent.manage_beforeDelete(self, item, container)
		# if content is a vector, delete whole directory
		dirPath = IMGconvert.makePath('', item.getPhysicalPath())
		try:
		   os.system('rm -R ' + dirPath)
		except:
		   pass

#	at_post_create_script = postCreateScript
 	at_post_edit_script = postEditScript

	##
	## Protected Functions 
	##
	# Dynamically finds mapfile
	# Makes calculations and allocations if it is the first time viewing
	security.declareProtected(permissions.View, "getMapPath")
        def getMapPath(self):
		mapFile = str(self.getFilename('mapFile'))
		writeDir = self.getPhysicalPath()
		customMapFile = IMGconvert.makePath('leam.'+mapFile, writeDir) 
		# If this is the first run, create the needed files
		if os.path.exists(customMapFile):
		    pass
		else: # first time run
		    image = str(self.getFilename('simImage'))
		    location=self.getLocation()
		    if self.getLatlong() == '':
	               self.latlong = IMGconvert.createFiles(image, mapFile, writeDir, location)
                    else:
                       IMGconvert.createFiles(image, mapFile, writeDir, location)
		return customMapFile

	# Pull the markers from the mapfile
	# Have simmap_view.pt read the markers and display them
	security.declareProtected(permissions.View, "getMarkers")
        def getMarkers(self):
		mapFile = str(self.getFilename('mapFile'))
		writeDir = self.getPhysicalPath()
		mapPath = IMGconvert.makePath('leam.'+mapFile, writeDir)
		output = ''
		f = open(self.getMapPath(), 'r') 
		for l in f:
		   if (l.find('COORD') != -1):
		      output = output + l.split('COORD')[1].strip() + '|'
		   elif (l.find('MESSAGE') != -1):
		      output = output + l.split('MESSAGE')[1].strip() + '|'
		if output != '':
		   output = output.strip('|')
		return output


	security.declareProtected(permissions.View, "linkAsHtml")
	def linkAsHtml(self, REQUEST, RESPONSE):
		"""The linkAsHtml page."""
		RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename="' + str(self.title) + '.html"')
		RESPONSE.setHeader('Content-Type', 'text/html')
		# Create HTML
		out = '<html><head><title>' + str(self.title) + '</title></head><body>'
		out = out + '<H1>' + str(self.title) + '</H1><a href="' + self.access_mode + str(self.path) + '/results_file"> OpenBlah </a></body></html>'
		RESPONSE.write(str(out))

## Register the new type within Zope
#registerType(SimMap,PROJECTNAME)



atapi.registerType(simmap, PROJECTNAME)

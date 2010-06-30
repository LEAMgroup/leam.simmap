#
# SimMap
#  A Map Simulation Content Type for Plone
#
# SimMap.py
#  The Product
#
# Author: Christian Koller <admin@iecw.net>
#         James Common, Richard Trieu, John Wang, Paul Yuan
#         John Layman, Kora Bongen, Lawrence Han, Shawn Sethi
#
# Released under GNU GPL v2 or later
#

from persistent import Persistent
from Products.Archetypes.atapi import *
from Products.Archetypes.interfaces import *
from Products.CMFCore import permissions
try:
    from iw.fss.FileSystemStorage import FileSystemStorage
except ImportError:
    from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage
from Products.validation import V_REQUIRED
from AccessControl import ClassSecurityInfo
from Products.SimMap.config import PROJECTNAME, PROTOCOLS
from zope.component import adapter

import os
import IMGconvert
class SimMap(BaseContent):	
	""" A Simulation Map Content Type """
	
	meta_type = portal_type = PROJECTNAME
	archetype_name = PROJECTNAME
	_at_rename_after_creation = True
	
        security  = ClassSecurityInfo()

	schema = BaseSchema.copy() + Schema((

                 StringField('Description',
                             searchable = 1,
                             required = 0,
                             isMetadata = True,
                             widget = StringWidget(label = 'Description', size = 45),
                             ),
                 FileField('simImage',
                           searchable = 0,
                           required = 1,
                           storage = FileSystemStorage(),
                           widget = FileWidget(label = 'Simulation Image')
                           ),
                           
                 FileField('mapFile',
                           searchable = 0,
                           required = 1,
                           storage = FileSystemStorage(),
                           widget = FileWidget(label = 'Map File')
                           ),
                 StringField('location',
                           searchable = 0,
                           required = 0,
                           isMetadata = True,
                           widget = StringWidget(label= "Grass Location (specify to upload to GRASS, otherwise leave blank)", size=20)
                           ),
                 FloatField('Transparency',
                            searchable = 0,
                            required = 1,
                            default = 0.7,
                            isMetaData = True,
                            widget = StringWidget(label = 'Transparency', size = 4, description = '0.0 = Transparent 1.0 = Opaque')
                            ),
                 StringField('latlong',
                             searchable = 0,
                             required = 0,
                             widget = StringWidget(label = 'Lat/Long (must be formatted as: "lat long")', size = 50),
                          ),
		 IntegerField('zoom',
                             searchable = 0,
                             required = 1,
                             default = 11,
                             widget = IntegerWidget(label = 'Zoom Level', description = '0 = No Zoom, 19 = Full Zoom', size = 2),
                            ),
                 TextField('details',
                           searchable = 1,
                           required = 0,
                           default_output_type = 'text/html',
                           default_content_type = 'text/html',
                           widget = RichWidget(allow_file_upload = False, label = 'Details')
                           ),
	))

	##
	##  Redefine the view tab (action) for SimMap
	##
	actions = (
		{
			'id': 'view',
			'name': 'View',
			'action': 'string:${object_url}',
			'permissions': (permissions.View,)
		},
		{
			'id' : 'edit',
			'name' : 'Edit',
			'action' : 'string:${object_url}/edit',
			'permissions' : (permissions.ModifyPortalContent,),
		},
		{
			'id' : 'metadata',
			'name' : 'Properties',
			'action' : 'string:${object_url}/properties',
			'permissions' : (permissions.ModifyPortalContent,),
		},
	)

	aliases = {
		'(Default)'  : 'simmap_view',
		'view'       : 'simmap_view',
		'edit'       : 'base_edit',
		'properties' : 'base_metadata',
		}

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
registerType(SimMap,PROJECTNAME)

"""Definition of the simmap content type
"""

from zope.interface import implements, directlyProvides

from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from iw.fss.FileSystemStorage import FileSystemStorage

from leam.simmap import simmapMessageFactory as _
from leam.simmap.interfaces import ISimMap
from leam.simmap.config import PROJECTNAME

import os
import zipfile

simmapSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.FileField( 'simImage',
        storage=FileSystemStorage(),
        widget=atapi.FileWidget(
            label=_(u"GIS Layer"),
            description=_(u""),
        ),
        required=True,
        validators=('isNonEmptyFile'),
    ),


    atapi.FileField( 'mapFile',
        storage=FileSystemStorage(),
        widget=atapi.FileWidget(
            label=_(u"Mapserver Map File"),
            description=_(u""),
        ),
        #validators=('isNonEmptyFile'),
    ),


    atapi.TextField('details',
        storage=atapi.AnnotationStorage(),
        default_content_type='text/html',
        allowable_content_type='(text/html, text/plain)',
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u"Details"),
            description=_(u"Description of GIS Layer"),
        ),
    ),


    atapi.FloatField( 'transparency',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Transparency"),
            description=_(u"0.0 = transparent, 1.0 = opaque"),
        ),
        default = 0.7,
        validators = ('isDecimal'),
    ),


    atapi.StringField('latlong',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Latitude Longitude"),
            description=_(u'formatted as "lat long"'),
        ),
        required=False,
    ),

    atapi.IntegerField('zoom',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Zoom Level"),
            description=_(u"0 = No Zoom, 19 = Full Zoom"),
        ),
        default = 10,
        validators = ('isInt'),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

simmapSchema['title'].storage = atapi.AnnotationStorage()
simmapSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(simmapSchema, moveDiscussion=False)


def removeLEAM(simmap, event):
    """Remove the LEAM specific version of the simmap files from the FSS
    managed directory. This is generally called after simmap edits to 
    rebuild the mapfile and leam.files directory.
    """
    p = os.path.split(simmap.getSimImage().path)[0]
    os.system('rm -rf %s/leam.*' % p)
    

class SimMap(base.ATCTContent):
    """SimMap version 2"""
    implements(ISimMap)

    meta_type = "SimMap"
    schema = simmapSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    simImage = atapi.ATFieldProperty('simImage')
    mapFile = atapi.ATFieldProperty('mapFile')
    details = atapi.ATFieldProperty('details')
    transparency = atapi.ATFieldProperty('transparency')
    latlong = atapi.ATFieldProperty('latlong')
    zoom = atapi.ATFieldProperty('zoom')


    def _extract_layer(self, src):
        """Attmpts to unzip the <src> file and save files to disk.  If <src>
           is not a zip file no changes are made on the file system.
           _extract_layer returns the name of the layer (filename only)
           appropriate for modifying the mapfile DATA parameter.
        """

        path, layer = os.path.split(src)
        myfiles = os.path.join(path, 'leam.files')

        try:
            if os.path.exists(myfiles):
                os.system('rm -rf %s' % myfiles)
            os.mkdir(myfiles)

            zip = zipfile.ZipFile(open(src, 'r'))
            for fname in zip.namelist():

                # skip any directories within the zipfile
                if fname.endswith('/'):
                    continue

                # save all normal files in lower case!
                ofile = os.path.join(myfiles, os.path.basename(fname).lower())
                f = open(ofile, 'wb')
                f.write(zip.read(fname))
                f.close()

                # save the outfile name if it's the primary file
                n, ext = os.path.splitext(ofile)
                if ext in ['.shp', '.tif', '.img']:
                    layer = os.path.join('leam.files', ofile)

        # if it's not a zip file, we assume it's a valid GIS layer
        except zipfile.BadZipfile:
            pass

        return layer


    def _create_files(self, image, mapfile):
        """_create_files is responsible for unpacking any compressed
           image files (using _try_unzip) and creating a custom mapfile
           that has the DATA field modified to point to the local files.
           Modified mapfile will be named with 'leam.' filename prefix.

           <image> is the absolute path to the GIS layer being imported.
           <mapfile> is the absoluate path to the mapfile.
        """
        layer = self._extract_layer(image)

        path, mapname = os.path.split(mapfile)
        mymap = os.path.join(path, 'leam.'+mapname)

        mapout = open(mymap, 'w')
        mapin = open(mapfile)
        for l in mapin:
            indent = l.find('DATA')
            if l.find('DATA') == -1:
                mapout.write(l)
            else:
                mapout.write('%sDATA "%s"\n' % (' '*indent, layer))
        mapin.close()
        mapout.close()


    def _calc_latlong(self, mapPath):
        # Seeks through a map file and finds the EXTENT field
        # Once found, it calculates a center lat and long and returns it
        # Relevant line is in form: lat long
        mapfile = open(mapPath, 'r')
        for l in mapfile:
            if l.find('EXTENT') != -1:
                 coordArray = l.split('EXTENT ')
                 coordArray = coordArray[1].split(' ')
                 long = (float(coordArray[0]) + float(coordArray[2]))/2
                 lat = (float(coordArray[1]) + float(coordArray[3]))/2
                 break
            else:
                continue
        return '%s %s'%(lat,long)


    # Dynamically finds mapfile
    # Makes calculations and allocations if it is the first time viewing
    #security.declareProtected(permissions.View, "getMapPath")
    security.declarePublic("getMapPath")
    def getMapPath(self):
        """returns the file system path to the Simmap mapFile"""
        #import pdb; pdb.set_trace()

        path, mapfile = os.path.split(self.getMapFile().path)
        mymap = os.path.join(path, 'leam.'+mapfile)

        # If this is the first run, create the needed files
        if not os.path.exists(mymap):
            self._create_files(self.getSimImage().path, self.getMapFile().path)
        if not self.getLatlong():
            self.setLatlong(self._calc_latlong(mymap))

        return mymap

    security.declarePublic("get_mapserve")
    def get_mapserve(self, REQUEST, RESPONSE):
        """redirects to the mapserver to aid in debugging"""
        mymap = self.getMapPath()
        RESPONSE.redirect("http://plone.leamgroup.com/cgi-bin/mapserv?mode=map&map=%s" % mymap)
        

    #security.declareProtected(permissions.View, "get_layer")
    security.declarePublic("get_layer")
    def get_layer(self, REQUEST, RESPONSE):
        """Download the GIS Layer"""

        RESPONSE.redirect(context.absolute_url()+'/at_download/simImage')
        return
        #RESPONSE.setHeader('X-Sendfile', p);
        #RESPONSE.setHeader('Content-Type', 'application/octet-stream')
        #RESPONSE.setHeader('Content-Disposition',
        #      'attachment; filename="' + str(os.path.basename(p)) + '"')

    #security.declareProtected(permissions.View, "get_mapfile")
    security.declarePublic("get_mapfile")
    def get_mapfile(self, REQUEST, RESPONSE):
        """Download the mapfile """

        RESPONSE.redirect(context.absolute_url()+'/at_download/mapFile')
        return
        #p = self.getMapFile().path
        #RESPONSE.setHeader('X-Sendfile', p);
        #RESPONSE.setHeader('Content-Type', 'text/plain')
        #RESPONSE.setHeader('Content-Disposition',
        #      'attachment; filename="' + str(os.path.basename(p)) + '"')


atapi.registerType(SimMap, PROJECTNAME)

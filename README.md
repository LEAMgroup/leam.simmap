## leam.simmap
Plone plugin that provides a custom content type that allows GIS layers
to uploaded directly to Plone and rendered as an overlay on basemaps.

#### Requirements
* iw.fss
* Mapserver

The iw.fss package
works something like Plone's native blob mechanism where fields can be
stored on the file system external to the Zope Database.  SimMaps takes
advantage of the file system layout and makes locally modified versions
of the necessary files to allow Mapserver to read and render the GIS
layers.

#### Installation

##### iw.fss
Add the following sections to your buildout.cfg.
```
eggs =
    Plone
    ...
    iw.fss==2.8.0rc5
    
zcml =
    iw.fss
    iw.fss-meta
    
parts = 
    ...
    fss
    
[fss]
recipe = iw.recipe.fss
storages =
    global /
    <site> /<site> site2
```
Where <site> is replaced with the Plone Sites short name.  

Note: The iw.fss package is no longer support but seems to still work as of Plone 4.3.3.

##### Mapserver
Mapserver can generally be installed using system repositories using
command like the following:
```
sudo apt-get install mapserver
```

#### History
SimMap is short for "simulation map" as leam.simmap was first used to
diplay the results of the LEAM land use change model.  It has now become
a generic tool for displaying GIS layers.


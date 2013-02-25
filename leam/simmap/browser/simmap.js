jq(window).bind('load', function() {
    var mapserv = jq('#map_mapserver').html();
    var mappath = jq('#map_mappath').html();
    var trans = jq('#map_transparency').html();
    var zoom = jq('#map_zoom').html();
    var ll = jq('#map_latlong').html();
    var arr = ll.split(' ');
    var lat = arr[0];
    var lon = arr[1];

    OpenLayers.ImgPath = "++resource++ol_images/";

    var options = {
        projection: "EPSG:900913",
        theme: null,
        //allOverlays: true,
        };
    olmap = new OpenLayers.Map('map', options);
    olmap.addControl(new OpenLayers.Control.LayerSwitcher());
    olmap.events.register('changelayer', null, function(evt) {

        // should update the legend here
        if (evt.property === "visibility") {
            var dummy = 0;
            //alert(evt.layer.map + " visibility changed");
        }
    });

    var blayer = new OpenLayers.Layer.Google("Google Map",
        { sphericalMercator: true,
          displayInLayerSwitcher: false,
        });
    olmap.addLayer(blayer);
    //var osm = new OpenLayers.Layer.OSM("Simple OSM");

    jq('.navTreeItem .contenttype-simmap').each(function() {
        var mappath = "";
        jq.ajax({
             url: jq(this).attr('href')+'/getMapPath',
             async: false,
             success: function(data) {
                 mappath=data;
             }
        });
        var simmap = new OpenLayers.Layer.WMS( 
            jq(this).find('span').text(),
            mapserv,
            { "map": mappath,
              sphericalMercator: true,
              transparent: true, 
              format: "image/png",
              layers: "final4",
            },
            {
              isBaseLayer: false, 
              opacity: trans,
              visibility: jq(this).hasClass('navTreeCurrentNode'),
            });
        olmap.addLayer(simmap);
    });

    olmap.setCenter(new OpenLayers.LonLat(lon, lat).transform(
       new OpenLayers.Projection("EPSG:4326"),
       olmap.getProjectionObject()), zoom);    
    }
);

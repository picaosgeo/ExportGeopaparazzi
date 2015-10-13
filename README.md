ExportGeopaparazzi
==========================

If you encountered problems with Kmzgeopapaimport and GeopaparazziTags converter, try this minimal plugin.
Look for your *.gpap file in your harddisk and it will export the point layers (notes, image positions and bookmarks) in separated *.csv files, images in a new "images" folder and tracklogs in separate *.kml files, all in the same directory of the Geopaparazzi database.
The CSV files can be loaded in QGIS with the "Add Delimited Text Layer" tool. The Lon and lat fields are automatically recognized. After that, it will ask you to choose the right CRS that is WGS84 (i.e. EPSG: 4326).
The KML file will be loaded directly by the "Add Vector Layer" tool (remember to choose the rigth file format!)
You can contact me by email at the address: enrico.chiaradia@yahoo.it


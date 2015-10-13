"""
/***************************************************************************
Name			 	 : __init__.py
Description          : Just another Geopaparazzi database exporter
Date                 : 12/Oct/15 
copyright            : (C) 2015 by Enrico A. Chiaradia
email                : enrico.chiaradia@yahoo.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General self.License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
def name(): 
  return "Export Geopaparazzi" 
def description():
  return "Just another Geopaparazzi database exporter"
def version(): 
  return "Version 0.1" 
def qgisMinimumVersion():
  return "2.0"
def classFactory(iface): 
  from ExportGeopaparazzi import ExportGeopaparazzi 
  return ExportGeopaparazzi(iface)

#!/usr/bin/python
"""
/***************************************************************************
Name			 	 : ExportDataset.py
Description : Just another Geopaparazzi database exporter
Date          : 12/Oct/15 
copyright   : (C) 2015 by Enrico A. Chiaradia
email         : enrico.chiaradia@yahoo.it 
credits       :
http://geospatialpython.com/2015/05/geolocating-photos-in-qgis.html
http://linfiniti.com/2012/03/a-python-layer-action-to-open-a-wikipedia-page-in-qgis/
http://gis.stackexchange.com/questions/60473/how-can-i-programatically-create-and-add-features-to-a-memory-layer-in-qgis-1-9


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
import sqlite3 as sqlite
import os
import optparse
from osgeo import ogr
from Table import Table

from qgis.core import *
from qgis.gui import *

from PyQt4.QtCore import QVariant  

def exportPointToTempVector(pointTable,layName='pointlist', fields = None):
  # create layer
  vl = QgsVectorLayer("Point?crs=EPSG:4326", layName, "memory")
  pr = vl.dataProvider()

  # changes are only possible when editing the layer
  vl.startEditing()
  # add fields
  pr.addAttributes(fields)

  # add a features
  for r in range(0,pointTable.getNumOfRec()):
    lon = float(pointTable.getValue('lon',r))
    lat = float(pointTable.getValue('lat',r))
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(lon,lat)))
    fet.setAttributes(pointTable.getRecord(r))
    pr.addFeatures([fet])

  # commit to stop editing the layer
  vl.commitChanges()

  # update layer's extent when new features have been added
  # because change of extent in provider is not propagated to the layer
  vl.updateExtents()
  
  return vl
  
def exportLineToTempVector(pointTable,layName='line', fields = None):
  # create layer
  vl = QgsVectorLayer("LineString?crs=EPSG:4326", layName, "memory")
  pr = vl.dataProvider()

  # changes are only possible when editing the layer
  vl.startEditing()
  # add fields
  pr.addAttributes(fields)

  # add a features
  pointList = []
  for r in range(0,pointTable.getNumOfRec()):
    #print pointTable.getValue('lon',r)
    lon = float(pointTable.getValue('lon',r))
    lat = float(pointTable.getValue('lat',r))
    pointList.append(QgsPoint(lon,lat))
  
  fet = QgsFeature()
  fet.setGeometry(QgsGeometry.fromPolyline(pointList))
  #fet.setAttributes(pointTable.getRecord(r))
  pr.addFeatures([fet])

  # commit to stop editing the layer
  vl.commitChanges()

  # update layer's extent when new features have been added
  # because change of extent in provider is not propagated to the layer
  vl.updateExtents()
  
  return vl

  
def convertToStringList(datalist):
  strList = []
  for e in datalist:
    if isinstance(e, basestring):
      strList.append(e.encode('utf8'))
    else:
      strList.append(str(e))
  
  return strList

def ExportDataset(pathToDB, DBname,currentPath):
  # connect to database
  con = sqlite.connect(pathToDB+'\\'+DBname)
  cur = con.cursor()
  #create a table with notes
  # "_id","lon","lat","altim","ts","description","text","form","style","isdirty"
  notes = cur.execute("SELECT * FROM notes")
  notesTable = Table(["_id","lon","lat","altim","ts","description","text","form","style","isdirty"])
  notesTableFields = [QgsField("_id", QVariant.Int), QgsField("lon", QVariant.Double), QgsField("lat", QVariant.Double),QgsField("altim", QVariant.Double), \
                                      QgsField("ts", QVariant.String),QgsField("description", QVariant.String), \
                                      QgsField("form", QVariant.String),QgsField("style", QVariant.String), \
                                      QgsField("isdirty", QVariant.Int)]
                                      
  for note in notes:
    note = convertToStringList(note)
    notesTable.addRecordList(note)
    
  vl = exportPointToTempVector(notesTable, layName='notes', fields = notesTableFields)
  vl.loadNamedStyle(currentPath+'/styles/note_symb.qml')
  # add to the TOC
  QgsMapLayerRegistry.instance().addMapLayer(vl)

  #create a table with image positions
  images = cur.execute("SELECT * FROM images")
  imagesTable = Table(["_id","lon","lat","altim","azim","imagedata_id","ts","text","note_id","isdirty"])
  imagesTableFields = [QgsField("_id", QVariant.Int), QgsField("lon", QVariant.Double), QgsField("lat", QVariant.Double),QgsField("altim", QVariant.Double),QgsField("azim", QVariant.Double), \
                                      QgsField("imagedata_id", QVariant.Int),QgsField("ts", QVariant.String),QgsField("text", QVariant.String), \
                                      QgsField("note_id", QVariant.Int), QgsField("isdirty", QVariant.Int)]
 
  for img in images:
    img = convertToStringList(img)
    imagesTable.addRecordList(img)
    
  vl = exportPointToTempVector(imagesTable, layName='image positions', fields = imagesTableFields)
  vl.loadNamedStyle(currentPath+'/styles/image_symb.qml')
  # add Show Image Action
  SIact = 'from PyQt4.QtCore import QUrl; from PyQt4.QtWebKit import QWebView;  myWV = QWebView(None); '
  SIact += 'myWV.setWindowTitle('+'"'+'[% "text" %]'+'"'+'); '
  SIact += 'myWV.load(QUrl('
  SIact += "'"+pathToDB+'\images\[% "text" %]'+"'"+")); myWV.show()"
  # SIact = pathToDB+'\images\[% "text" %]'
  # actions.addAction(QgsAction.OpenUrl, "Show Image",SIact)
  actions = vl.actions()
  actions.addAction(QgsAction.GenericPython, "Show Image",SIact)

  # add to the TOC
  QgsMapLayerRegistry.instance().addMapLayer(vl)

  #create a table with bookmarks
  bookmarks = cur.execute("SELECT * FROM bookmarks")
  bookmarksTable = Table(["_id","lon","lat","zoom","bnorth","bsouth","bwest","beast","text"])
  bookmarksTableFields = [QgsField("_id", QVariant.Int), QgsField("lon", QVariant.Double), QgsField("lat", QVariant.Double), \
                                      QgsField("zoom", QVariant.Double),QgsField("bnorth", QVariant.Double), \
                                      QgsField("bsouth", QVariant.Double),QgsField("bwest", QVariant.Double), \
                                      QgsField("beast", QVariant.Double),QgsField("text", QVariant.String)]
 
  for bkm in bookmarks:
    bkm = convertToStringList(bkm)
    bookmarksTable.addRecordList(bkm)
    
  vl = exportPointToTempVector(bookmarksTable, layName='bookmarks', fields = bookmarksTableFields)
  vl.loadNamedStyle(currentPath+'/styles/bookmark_symb.qml')
  # add to the TOC
  QgsMapLayerRegistry.instance().addMapLayer(vl)
  
  #create a new folder with images inside
  if not os.path.isdir(pathToDB+'\\'+'images'):
    os.makedirs(pathToDB+'\\'+'images')
  
  # get the list of images
  imgIDs = imagesTable.getColumn("_id")
  imgNames = imagesTable.getColumn("text")
  
  # loop in the list and get BLOB
  i = 0
  for imgID in imgIDs:
    imgsData = cur.execute("SELECT * FROM imagedata WHERE _id = " + str(imgID))
    imgName = imgNames[i]
    #print imgID, imgName
    
    for imgData in imgsData:
      with open(pathToDB+'\\'+'images'+ '\\' + imgName, "wb") as output_file:
        output_file.write(imgData[1])
    i +=1

  #create a table with logs
  gpslogs = cur.execute("SELECT * FROM gpslogs") 
  gpslogsTable = Table(["_id","startts","endts","lengthm","isdirty","text"])
  gpslogsTableFields = [QgsField("_id", QVariant.Int), QgsField("startts", QVariant.Double), QgsField("endts", QVariant.Double), \
                                      QgsField("lengthm", QVariant.Double),QgsField("isdirty", QVariant.Int),QgsField("text", QVariant.String)]
  # load the list of gpslogs
  for l in gpslogs:
    l = convertToStringList(l)
    gpslogsTable.addRecordList(l)
  
  # create layer
  vl = QgsVectorLayer("LineString?crs=EPSG:4326", 'tracklogs', "memory")
  pr = vl.dataProvider()

  # changes are only possible when editing the layer
  vl.startEditing()
  # add fields
  pr.addAttributes(gpslogsTableFields)
  
  #create a line for each logs
  for r in range(0,gpslogsTable.getNumOfRec()):
    logID = str(gpslogsTable.getValue('_id',r))
    logname = str(gpslogsTable.getValue('text',r))
    #print logID, logname
    gpslogData  = cur.execute("SELECT * FROM gpslogsdata WHERE logid = " + logID + " ORDER BY _id")
    gpslogTable = Table(["_id","lon","lat","altim","ts","logid"])
    
    for gpslogd in gpslogData:
      gpslogd = convertToStringList(gpslogd)
      gpslogTable.addRecordList(gpslogd)
    
    # add a features
    pointList = []
    for g in range(0,gpslogTable.getNumOfRec()):
      #print pointTable.getValue('lon',r)
      lon = float(gpslogTable.getValue('lon',g))
      lat = float(gpslogTable.getValue('lat',g))
      pointList.append(QgsPoint(lon,lat))
    
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPolyline(pointList))
    fet.setAttributes(gpslogsTable.getRecord(r))
    pr.addFeatures([fet])

    # commit to stop editing the layer
    vl.commitChanges()

    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    vl.updateExtents()
    vl.loadNamedStyle(currentPath+'/styles/tracklog_symb.qml')
    # add to the TOC
    QgsMapLayerRegistry.instance().addMapLayer(vl)
    
  #close connection
  cur.close()
  con.close()

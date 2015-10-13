#!/usr/bin/python
"""
/***************************************************************************
Name			 	 : ExportDataset.py
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
import sqlite3 as sqlite
import os
import optparse
from osgeo import ogr
from Table import Table

def exportPointToKML(pointTable, filename,layName='pointlist'):
  ds = ogr.GetDriverByName('KML').CreateDataSource(filename)
  lyr = ds.CreateLayer(layName)
  # add field
  for fld in pointTable.fldName:
      lyr.CreateField(ogr.FieldDefn(fld, ogr.OFTString))
      
  # loop in pointTable and save points
  for r in range(0,pointTable.getNumOfRec()):
    rec = pointTable.lod[r]
    #print rec
    dst_feat = ogr.Feature( lyr.GetLayerDefn() )
    lon = rec['lon']
    lat = rec['lat']
    dst_feat.SetField('name', rec['text'])
    dst_feat.SetField('description', rec['azim'])
    for fld in pointTable.fldName:
      dst_feat.SetField(fld, rec[fld])
      
    dst_feat.SetGeometry(ogr.CreateGeometryFromWkt('POINT ('+lon+' '+lat+')'))
    if lyr.CreateFeature( dst_feat ) != 0:
      gdaltest.post_reason('CreateFeature failed.')
      return 'fail'
      
def exportLineToKML(pointTable, filename,layName='trace'):
  ds = ogr.GetDriverByName('KML').CreateDataSource(filename)
  lyr = ds.CreateLayer(layName)

  wkt = 'LINESTRING ('
  # add points coordinates
  for r in range(0,pointTable.getNumOfRec()):
    rec = pointTable.lod[r]
    lon = rec['lon']
    lat = rec['lat']
    alt = rec['altim']
    pointStr = lon + ' ' + lat + ' '+ alt
    wkt = wkt+pointStr+','
    
  # remove last character and add brake
  wkt = wkt[:-1]
  wkt = wkt +')'
  
  dst_feat = ogr.Feature( lyr.GetLayerDefn() )
  dst_feat.SetField('name', layName)
  dst_feat.SetField('description', layName)
  dst_feat.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
  if lyr.CreateFeature( dst_feat ) != 0:
    gdaltest.post_reason('CreateFeature failed.')
    return 'fail'

def createPointSF(pointTable, filename):
  #shpDriver = ogr.GetDriverByName( "ESRI Shapefile" )
  ##delete old file if exists
  #if os.path.exists(filename):
  #  shpDriver.DeleteDataSource(filename)
  
  #shpDS = shpDriver.CreateDataSource(filename)
  #pointLayer = shpDS.CreateLayer( 'point', None, ogr.wkbPoint )
  #for fld in pointTable.fldName:
  #  # add fields
   # fd = ogr.FieldDefn( 'ID', ogr.OFTString )
   # pointLayer.CreateField( fd )
  
  # add point to shapefile
  pass

def createLineSF():
  pass
  
def convertToStringList(datalist):
  strList = []
  for e in datalist:
    strList.append(str(e))
  
  return strList

def ExportDataset(pathToDB, DBname):
  # connect to database
  con = sqlite.connect(pathToDB+'\\'+DBname)
  cur = con.cursor()
  #create a table with notes
  # "_id","lon","lat","altim","ts","description","text","form","style","isdirty"
  notes = cur.execute("SELECT * FROM notes")
  notesTable = Table(["_id","lon","lat","altim","ts","description","text","form","style","isdirty"])
  for note in notes:
    note = convertToStringList(note)
    notesTable.addRecordList(note)
    
  notesTable.saveLod(pathToDB+'\\'+'notes.csv')

  #create a table with image positions
  images = cur.execute("SELECT * FROM images")
  imagesTable = Table(["_id","lon","lat","altim","azim","imagedata_id","ts","text","note_id","isdirty"])
 
  for img in images:
    img = convertToStringList(img)
    imagesTable.addRecordList(img)
    
  imagesTable.saveLod(pathToDB+'\\'+'images.csv')
  #exportPointToKML(imagesTable,pathToDB+'\\'+'images.kml','images')
  
  #create a table with bookmarks
  bookmarks = cur.execute("SELECT * FROM bookmarks")
  bookmarksTable = Table(["_id","lon","lat","zoom","bnorth","bsouth","bwest","beast","text"])
 
  for bkm in bookmarks:
    bkm = convertToStringList(bkm)
    bookmarksTable.addRecordList(bkm)
    
  bookmarksTable.saveLod(pathToDB+'\\'+'bookmarks.csv')
  
  #create a new folder with images inside
  if not os.path.isdir(pathToDB+'\\'+'images'):
    os.makedirs(pathToDB+'\\'+'images')
  
  imagesData = cur.execute("SELECT * FROM imagedata") 
  for imgData in imagesData:
    imgID = str(imgData[0])
    # get the name of the image
    row = imagesTable.lookupLod(imagedata_id=imgID)
    with open(pathToDB+'\\'+'images'+ '\\' + str(row['text']), "wb") as output_file:
      output_file.write(imgData[1])


  #create a table with logs
  gpslogs = cur.execute("SELECT * FROM gpslogs") 
  gpslogsTable = Table(["_id","startts","endts","lengthm","isdirty","text"])
  for l in gpslogs:
    l = convertToStringList(l)
    gpslogsTable.addRecordList(l)
  
  #create and save KML file for each logs
  for r in range(0,gpslogsTable.getNumOfRec()):
    rec = gpslogsTable.lod[r]
    logID = str(rec['_id'])
    logname = str(rec['text'])
    print logID, logname
    gpslogData  = cur.execute("SELECT * FROM gpslogsdata WHERE logid = " + logID + " ORDER BY _id")
    gpslogTable = Table(["_id","lon","lat","altim","ts","logid"])
    for gpslogd in gpslogData:
      gpslogd = convertToStringList(gpslogd)
      gpslogTable.addRecordList(gpslogd)
      
    exportLineToKML(gpslogTable,pathToDB+'\\' +logname+'.kml',logname)
    
  #close connection
  cur.close()
  con.close()

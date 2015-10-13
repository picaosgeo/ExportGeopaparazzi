"""
/***************************************************************************
Name			 	 : Table.py
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
import csv

class Table: 
  def __init__(self,fldName):
    self.lod = [] # "list of dicts"
    self.fldName = fldName # a list of field Name
    
  def addRecord(self, newRecord):
    self.lod.append(newRecord)
    
  def addRecordList(self, newRecord):
    recDict = {}
    i = 0
    for fld in self.fldName:
      recDict[fld] = newRecord[i]
      i+=1
    
    self.addRecord(recDict)

  def populateLod(self, csv_fp, sep =','):
    with open(csv_fp, 'r') as f:  # Just use 'w' mode in 3.x
      rdr = csv.DictReader(f, self.fldName,delimiter=sep)
      self.lod.extend(rdr)

  def saveLod(self, csv_fp):
    with open(csv_fp, 'wb') as f:  # Just use 'w' mode in 3.x
      w = csv.DictWriter(f, self.fldName)
      w.writeheader()
      w.writerows(self.lod)
      
  def copyf(self, key, valuelist):
    lod = [dictio for dictio in self.lod if dictio[key] in valuelist]
    tableLod = Table(self.fldName)
    tableLod.lod.extend(lod)
    return tableLod
    
  def getColumn(self,key):
    return [x[key] for x in self.lod]
    
  def getNumOfRec(self):
    return len(self.lod)
    
  def getNumOfFields(self):
    return len(self.fldName)

# from the web ...
  def queryLod(self, filter=None, sort_keys=None):
    if filter is not None:
      lod = (r for r in self.lod if filter(r))
    if sort_keys is not None:
      lod = sorted(lod, key=lambda r:[r[k] for k in sort_keys])
    else:
      lod = list(self.lod)
    
    tableLod = Table(self.fldName)
    tableLod.lod.extend(lod)
    return tableLod

  def lookupLod(self,**kw):
    for row in self.lod:
        for k,v in kw.iteritems():
            if row[k] != str(v): break
        else:
            return row
    return None
    
  def updateField(self,fieldName, recNum, newValue):
    self.lod[recNum][fieldName] = newValue
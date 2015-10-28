# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name			 	 : ExportGeopaparazzi.py
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
#import resources
from tools.ExportDataset import ExportDataset

import os.path as osp
import sys

#setting the path variable for icon
currentpath = osp.dirname(sys.modules[__name__].__file__)

class ExportGeopaparazzi: 

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface
    # refernce to map canvas
    self.canvas = self.iface.mapCanvas()
    
  def initGui(self):
    # Create action that will start plugin
    self.action = QAction(QIcon(currentpath+'/images/Export dataset.png'), "&Export Dataset", self.iface.mainWindow())
    # connect the action to the run method
    QObject.connect(self.action, SIGNAL("activated()"), self.openExportDatasetGUI)
    # Add toolbar button and menu item
    self.iface.addPluginToMenu("ExportGeopaparazzi", self.action)

  def unload(self):
      # Remove the plugin menu item and icon
      self.iface.removePluginMenu("ExportGeopaparazzi",self.action)
    
  def openExportDatasetGUI(self):
    # get the path and the filename of geopaparazzi db
    path = QFileDialog.getOpenFileName(None, "Open Geopaparazzi Database File", "", "Geopaparazzi DB (*.gpap)")
    if path == '':
      return
      
    pathToDB = osp.dirname(path)
    DBname = osp.basename(path)
    # run export dataset function
    ExportDataset(pathToDB, DBname)
    # get list of layers with some metadata
    QMessageBox.information(self.canvas, "ExportGeopaparazzi", 'The export was completed successfully!')

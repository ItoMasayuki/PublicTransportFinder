# -*- coding: utf-8 -*-

import os
import re
import threading
import time
from PyQt4 import QtCore
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class PublicTransportFinder:

  def __init__(self, iface):
    self.iface = iface
    
    self.lock = threading.Lock()
    

    self.calc = None
    self.cat_db = None
    self.timetable = None
    self.thread = None
    self.worker = None

  def initGui(self):
    # initialize locale 
    locale = QSettings().value('locale/userLocale')
    if not locale: locale = 'en'
    else: locale = locale[0:2]
    locale_path = os.path.join( 
      os.path.dirname(__file__), 
      'i18n', 
      'PublicTransportFinder_{}.qm'.format(locale)) 
    if os.path.exists(locale_path): 
      self.translator = QTranslator() 
      self.translator.load(locale_path) 
      if qVersion() > '4.3.3': 
        QCoreApplication.installTranslator(self.translator) 

    path = os.path.dirname( os.path.abspath( __file__ ) )
    self.dock = uic.loadUi( os.path.join( path, "Dock.ui" ) )
    self.dlg = uic.loadUi( os.path.join( path, "Dialog.ui" ) )
    self.log = uic.loadUi( os.path.join( path, "Log.ui" ) )
    self.iface.addDockWidget( Qt.LeftDockWidgetArea, self.dock )
    self.clickTool = QgsMapToolEmitPoint(self.iface.mapCanvas()) 

    QObject.connect(self.dock.btnConf,SIGNAL("clicked()"),self.dockConfPressed)
    QObject.connect(self.dlg.btnOK,SIGNAL("clicked()"),self.dlgOKPressed)
    QObject.connect(self.dock.btnCalc,SIGNAL("clicked()"),self.dockCalcPressed)
    QObject.connect(self.dock.btnOrigin,SIGNAL("clicked()"),self.dockOriginClicked)
    QObject.connect(self.dock.btnDestination,SIGNAL("clicked()"),self.dockDestinationClicked)
#    QObject.connect(self.iface.mapCanvas(), SIGNAL('layersChanged()'), self.update_layers)
    QObject.connect(self.dlg.cmbTimetable,SIGNAL("currentIndexChanged(int)"),self.cmbTimetableChanged)
    QObject.connect(self.dlg.cmbTransit,SIGNAL("currentIndexChanged(int)"),self.cmbTransitChanged)
    QObject.connect(self.dlg.cmbOrigin,SIGNAL("currentIndexChanged(int)"),self.cmbOriginChanged)
    QObject.connect(self.dlg.cmbDestination,SIGNAL("currentIndexChanged(int)"),self.cmbDestinationChanged)

    self.i_cmbTimetable   = 0
    self.i_cmbRouteid     = 0
    self.i_cmbCat         = 0
    self.i_cmbTime        = 0
    self.i_cmbCatName     = 0
    self.i_cmbRouteName   = 0
    self.i_cmbTransit     = 0
    self.i_cmbFromcat     = 0
    self.i_cmbTocat       = 0
    self.i_cmbTime2       = 0
    self.i_cmbOrigin      = 0
    self.i_cmbIdOrig      = 0
    self.i_cmbDestination = 0
    self.i_cmbIdDest      = 0


    # add to plugins toolbar
    try:
      self.action = QAction("Toggle visibility", self.iface.mainWindow())
      self.action.triggered.connect(self.toggleDock)
      self.iface.addPluginToMenu("&PublicTransportFinder", self.action)
    except:
      pass  # OK for testing


  def unload(self):
    """unload the plugin"""
    self.iface.removeDockWidget(self.dock)
    self.iface.removePluginMenu("PublicTransportFinder", self.action)

  def toggleDock(self):
    self.dock.setVisible(not self.dock.isVisible())
#    self.update_layers()

  def dockOriginClicked(self):
    QObject.connect(self.clickTool, \
      SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), \
      self.handleMouseDownOrig)
    self.iface.mapCanvas().setMapTool(self.clickTool)

  def dockDestinationClicked(self):
    QObject.connect(self.clickTool, \
      SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), \
      self.handleMouseDownDest)
    self.iface.mapCanvas().setMapTool(self.clickTool)
    
  def handleMouseDownOrig(self, point, button): 
    self.dock.qleOrigin.clear()
    self.dock.qleOrigin.insert( str(point.x()) + "," +str(point.y()) )
    QObject.disconnect(self.clickTool, \
      SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), \
      self.handleMouseDownOrig)
    self.iface.mapCanvas().unsetMapTool(self.clickTool)
  def handleMouseDownDest(self, point, button): 
    self.dock.qleDestination.clear()
    self.dock.qleDestination.insert( str(point.x()) + "," +str(point.y()) )
    QObject.disconnect(self.clickTool, \
      SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), \
      self.handleMouseDownDest)
    self.iface.mapCanvas().unsetMapTool(self.clickTool)

  def dockConfPressed(self):
    self.dlg.setVisible(True)
    self.dlg.raise_()

    self.dlg.cmbTimetable.clear()
    self.dlg.cmbTransit.clear()
    self.dlg.cmbOrigin.clear()
    self.dlg.cmbDestination.clear()

    layers = self.iface.legendInterface().layers()
    layer_list = [QCoreApplication.translate('code', "Select an Item...")]
    for layer in layers:
#      if isinstance(layer, QgsVectorLayer) or \
#         isinstance(layer, QgsRasterLayer):
       layer_list.append(layer.name())
    self.dlg.cmbTimetable.addItems(layer_list)
    self.dlg.cmbTransit.addItems(layer_list)

    layer_list = [QCoreApplication.translate('code', "One by One")]
    for layer in layers: layer_list.append(layer.name())
    self.dlg.cmbOrigin.addItems(layer_list)
    self.dlg.cmbDestination.addItems(layer_list)
    
    if self.i_cmbTimetable == 0 and u"Timetable" in layer_list:
      self.i_cmbTimetable = layer_list.index(u"Timetable")
    if self.i_cmbTransit==0 and u"Transit" in layer_list:
      self.i_cmbTransit=layer_list.index(u"Transit")
    if self.i_cmbOrigin == 0 and u"Origin" in layer_list:
      self.i_cmbOrigin  = layer_list.index(u"Origin")
    if self.i_cmbDestination == 0 and u"Destination" in layer_list:
      self.i_cmbDestination = layer_list.index(u"Destination")
      
    self.dlg.cmbTimetable.setCurrentIndex(self.i_cmbTimetable)
    self.dlg.cmbRouteid.setCurrentIndex(self.i_cmbRouteid)
    self.dlg.cmbCat.setCurrentIndex(self.i_cmbCat)
    self.dlg.cmbTime.setCurrentIndex(self.i_cmbTime)
    self.dlg.cmbCatName.setCurrentIndex(self.i_cmbCatName)
    self.dlg.cmbRouteName.setCurrentIndex(self.i_cmbRouteName)
    self.dlg.cmbTransit.setCurrentIndex(self.i_cmbTransit)
    self.dlg.cmbFromcat.setCurrentIndex(self.i_cmbFromcat)
    self.dlg.cmbTocat.setCurrentIndex(self.i_cmbTocat)
    self.dlg.cmbTime2.setCurrentIndex(self.i_cmbTime2)
    self.dlg.cmbOrigin.setCurrentIndex(self.i_cmbOrigin)
    self.dlg.cmbIdOrig.setCurrentIndex(self.i_cmbIdOrig)
    self.dlg.cmbDestination.setCurrentIndex(self.i_cmbDestination)
    self.dlg.cmbIdDest.setCurrentIndex(self.i_cmbIdDest)


  def cmbTimetableChanged(self):
    if self.dlg.cmbTimetable.currentIndex() == 0:
      return
    layers = self.iface.legendInterface().layers()
    lTimeTable = layers[self.dlg.cmbTimetable.currentIndex()-1]
    
    self.dlg.cmbRouteid.clear()
    self.dlg.cmbCat.clear()
    self.dlg.cmbTime.clear()
    self.dlg.cmbCatName.clear()
    self.dlg.cmbRouteName.clear()
    flist = [QCoreApplication.translate('code', "Select an Item...")]
    for f in lTimeTable.pendingFields():
      flist.append(f.name())
    self.dlg.cmbRouteid.addItems(flist)
    self.dlg.cmbCat.addItems(flist)
    self.dlg.cmbTime.addItems(flist)
    self.dlg.cmbCatName.addItems(flist)
    self.dlg.cmbRouteName.addItems(flist)
    
    if self.i_cmbRouteid == 0 and u"route_id" in flist:
      self.i_cmbRouteid = flist.index(u"route_id")
    if self.i_cmbCat == 0 and u"cat" in flist:
      self.i_cmbCat = flist.index(u"cat")
    if self.i_cmbTime == 0 and u"time" in flist:
      self.i_cmbTime = flist.index(u"time")
    if self.i_cmbCatName == 0 and u"cat_name" in flist:
      self.i_cmbCatName = flist.index(u"cat_name")
    if self.i_cmbRouteName == 0 and u"route_name" in flist:
      self.i_cmbRouteName = flist.index(u"route_name")
    
    
    
  def cmbTransitChanged(self):
    if self.dlg.cmbTransit.currentIndex() == 0:
      return
    layers = self.iface.legendInterface().layers()
    lTransit = layers[self.dlg.cmbTransit.currentIndex()-1]
    
    self.dlg.cmbFromcat.clear()
    self.dlg.cmbTocat.clear()
    self.dlg.cmbTime2.clear()
    flist = [QCoreApplication.translate('code', "Select an Item...")]
    for f in lTransit.pendingFields():
      flist.append(f.name())
    self.dlg.cmbFromcat.addItems(flist)
    self.dlg.cmbTocat.addItems(flist)
    self.dlg.cmbTime2.addItems(flist)
    
    if self.i_cmbFromcat == 0 and u"from_cat" in flist:
      self.i_cmbFromcat = flist.index(u"from_cat")
    if self.i_cmbTocat == 0 and u"to_cat" in flist:
      self.i_cmbTocat = flist.index(u"to_cat")
    if self.i_cmbTime2 == 0 and u"time" in flist:
      self.i_cmbTime2 = flist.index(u"time")
    
    
  def cmbOriginChanged(self):
    if self.dlg.cmbOrigin.currentIndex() == 0:
      self.dlg.cmbIdOrig.clear()
      return

    layers = self.iface.legendInterface().layers()
    lOrigin = layers[self.dlg.cmbOrigin.currentIndex()-1]
    
    self.dlg.cmbIdOrig.clear()
    flist = [QCoreApplication.translate('code', "Select an Item...")]
    if lOrigin <> None:
      for f in lOrigin.pendingFields():
        flist.append(f.name())
    self.dlg.cmbIdOrig.addItems(flist)
    
    if self.i_cmbIdOrig == 0 and u"id" in flist:
      self.i_cmbIdOrig = flist.index(u"id")

  def cmbDestinationChanged(self):
    if self.dlg.cmbDestination.currentIndex() == 0:
      self.dlg.cmbIdDest.clear()
      return
    layers = self.iface.legendInterface().layers()
    lDestination = layers[self.dlg.cmbDestination.currentIndex()-1]
    
    self.dlg.cmbIdDest.clear()
    flist = [QCoreApplication.translate('code', "Select an Item...")]
    for f in lDestination.pendingFields():
      flist.append(f.name())
    self.dlg.cmbIdDest.addItems(flist)
    
    if self.i_cmbIdDest == 0 and u"id" in flist:
      self.i_cmbIdDest = flist.index(u"id")
    
  def dlgOKPressed(self):
    # 環境設定画面のＯＫボタンを押したとき
    self.dlg.setVisible(False)

    layers = self.iface.legendInterface().layers()
    lTimeTable = layers[self.dlg.cmbTimetable.currentIndex()-1]
    lTransit = layers[self.dlg.cmbTransit.currentIndex()-1]
    
    if not lTimeTable.isValid():
      self.myprint ("Layer failed to load!")
      return
    if not lTransit.isValid():
      self.myprint ("Layer failed to load!")
      return
      
    self.timetable = None
    from Timetable import Timetable
    self.timetable = Timetable(self)
    
    from CATDB import CATDB
    self.cat_db = CATDB(self)
    
    # 時刻表の設定
    for f in lTimeTable.getFeatures ():
#      self.myprint("add_timetable %d, %d, %f" % (
#        f[self.dlg.cmbRouteid.currentText()], \
#        f[self.dlg.cmbCat.currentText()], \
#        f[self.dlg.cmbTime.currentText()] ))
      catName = ""
      if self.dlg.cmbCatName.currentIndex() <> 0:
        catName = f[self.dlg.cmbCatName.currentText()]
      routeName = ""
      if self.dlg.cmbRouteName.currentIndex() <> 0:
        routeName = f[self.dlg.cmbRouteName.currentText()]

      ptn = re.compile('(\d+):(\d+)')
      m = ptn.match(f[self.dlg.cmbTime.currentText()])
      if m:
        tmp_time = (float(m.group(1))*60+float(m.group(2))) /1440.0
        # 深夜１２時～２時までは２４時から２６時に変換
        if tmp_time < 0.083333: tmp_time = tmp_time+1
      else:
        QMessageBox.information(None, "DEBUG:", "set time correctly") 

      self.timetable.add_timetable( \
        f[self.dlg.cmbRouteid.currentText()], \
        f[self.dlg.cmbCat.currentText()], \
        tmp_time, \
        routeName)
      self.cat_db.add_cat(f[self.dlg.cmbCat.currentText()], \
        f.geometry().asPoint().x(), \
        f.geometry().asPoint().y(), \
        catName)

    # 乗り換え表の設定
    for f in lTransit.getFeatures ():
      ptn = re.compile('(\d+):(\d+)')
      m = ptn.match(f[self.dlg.cmbTime2.currentText()])
      if m:
        tmp_time = (float(m.group(1))*60+float(m.group(2))) /1440.0
      else:
        QMessageBox.information(None, "DEBUG:", "set time correctly") 

      self.timetable.set_transit( \
        f[self.dlg.cmbFromcat.currentText()], \
        f[self.dlg.cmbTocat.currentText()], \
        tmp_time)

    self.myprint(QCoreApplication.translate('code', "Timetable, Transit table set")+u"\n")
    
    self.i_cmbTimetable   = self.dlg.cmbTimetable.currentIndex()
    self.i_cmbRouteid     = self.dlg.cmbRouteid.currentIndex()
    self.i_cmbCat         = self.dlg.cmbCat.currentIndex()
    self.i_cmbTime        = self.dlg.cmbTime.currentIndex()
    self.i_cmbCatName     = self.dlg.cmbCatName.currentIndex()
    self.i_cmbRouteName   = self.dlg.cmbRouteName.currentIndex()
    self.i_cmbTransit     = self.dlg.cmbTransit.currentIndex()
    self.i_cmbFromcat     = self.dlg.cmbFromcat.currentIndex()
    self.i_cmbTocat       = self.dlg.cmbTocat.currentIndex()
    self.i_cmbTime2       = self.dlg.cmbTime2.currentIndex()
    self.i_cmbOrigin      = self.dlg.cmbOrigin.currentIndex()
    self.i_cmbIdOrig      = self.dlg.cmbIdOrig.currentIndex()
    self.i_cmbDestination = self.dlg.cmbDestination.currentIndex()
    self.i_cmbIdDest      = self.dlg.cmbIdDest.currentIndex()
    
    

  def dockCalcPressed(self):
    self.log.setVisible(True)
    self.log.raise_()
    
    if self.timetable == None:
      self.dockConfPressed()
      return
      
    orig_list = []
    dest_list = []
    
    if self.dlg.cmbOrigin.currentIndex() <> 0:
      layers = self.iface.legendInterface().layers()
      lOrigin = layers[self.dlg.cmbOrigin.currentIndex()-1]
      if not lOrigin.isValid():
        self.myprint ("Layer failed to load!")
        return
      for f in lOrigin.getFeatures():
        orig_list.append((f[self.dlg.cmbIdOrig.currentText()],f.geometry().asPoint().x(), f.geometry().asPoint().y()))
    else:
      ptn = re.compile('([+-]?\d+\.?\d*) *?, *?([+-]?\d+\.?\d*)')
      m = ptn.match(self.dock.qleOrigin.text())
      if m:
        orig_list.append((0, float(m.group(1)),float(m.group(2))))
      else:
        QMessageBox.information(None, "DEBUG:", "set origin correctly") 

    if self.dlg.cmbDestination.currentIndex() <> 0:
      layers = self.iface.legendInterface().layers()
      lDestination = layers[self.dlg.cmbDestination.currentIndex()-1]
      if not lDestination.isValid():
        self.myprint ("Layer failed to load!")
        return
      for f in lDestination.getFeatures():
        dest_list.append((f[self.dlg.cmbIdDest.currentText()],f.geometry().asPoint().x(), f.geometry().asPoint().y()))
    else:
      ptn = re.compile('([+-]?\d+\.?\d*) *?, *?([+-]?\d+\.?\d*)')
      m = ptn.match(self.dock.qleDestination.text())
      if m:
        dest_list.append((0, float(m.group(1)),float(m.group(2))))
      else:
        QMessageBox.information(None, "DEBUG:", "set destination correctly") 
    
    ptn = re.compile('(\d+):(\d+)')
    m = ptn.match(self.dock.qleStartTime.text())
    if m:
      start_time = (float(m.group(1))*60+float(m.group(2))) /1440.0
    else:
      QMessageBox.information(None, "DEBUG:", "set start/arrive time correctly") 

    from CalculatorManager import CalculatorManager
    worker = self.worker = CalculatorManager(self)
    thread = self.thread = QtCore.QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    
    for o in orig_list:
      for d in dest_list:
        worker.qi.put((o[0], d[0] \
                      ,self.timetable \
                      ,self.cat_db
                      ,int(self.dock.qleSearchdirection.text()) \
                      ,300 \
                      ,o[1] ,o[2] ,d[1] ,d[2] \
                      , start_time))

    worker.myprintsignal.connect(self.myprint)
    thread.start()
    #worker.run()
        
    #self.myprint("started")

  def myprint(self,txt):
    self.log.ptxResult.appendPlainText(txt)
    
    
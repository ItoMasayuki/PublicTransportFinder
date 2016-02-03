# -*- coding: utf-8 -*-

from qgis.core import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
import time
import Queue

class CalculatorManager(QtCore.QObject):

  myprintsignal = QtCore.pyqtSignal(str)
  error = QtCore.pyqtSignal(Exception, basestring)

  def __init__(self,obj):
    QtCore.QObject.__init__(self)
    self.killed = False
    self.qi = Queue.Queue()
    self.parent = obj

  def run(self):
    start = time.time()
    
    self.myprint(QCoreApplication.translate('code', "Calculation Started."))
    
    while not self.qi.empty():

      (o0, d0, timetable, cat_db, direction, dist, ox, oy, dx, dy, start_time) = self.qi.get()
      
      calc = None
      from Calculator import Calculator

      calc = Calculator(self,timetable,cat_db)

      # 検索ごとに前回の検索内容を消去
      # 検索方法を設定 1:出発時刻指定  2:到着時刻指定
      calc.initialize(direction)

      # 出発点（駅番号：－１）と目的地（－２）をセット
      # 入力された緯度、経度から一定距離内にある駅を抽出する
      dist = 300
      
      buf = u"%s, %s, %f, %d, " % (o0, d0, start_time, direction)

      found_o, found_d = False, False
      for p,d in cat_db.get_cat(ox, oy, dist).items():
        calc.add_cost(-1, p, d/83*0.000694444)
        calc.add_cost(p, -1, d/83*0.000694444)
        found_o = True
      for p,d in cat_db.get_cat(dx, dy, dist).items():
        calc.add_cost(p, -2, d/83*0.000694444)
        calc.add_cost(-2, p, d/83*0.000694444)
        found_d = True
      
      if not found_o or not found_d:
        buf = buf + u"最寄りの交通機関が見つかりませんでした。"
      else:
        # 検索を実行する。
        # 引数は出発時刻、到着時刻のexcel時刻シリアル値
        buf = buf + calc.run( start_time )
        #calc.run( start_time )

      self.myprint(buf)

    elapsed_time = time.time() - start
    self.myprint ('elapsed time:' + "{0}".format(elapsed_time) + "[sec]")
    
    self.myprint(QCoreApplication.translate('code', "Calculation Finished.")+u"\n")

  def kill(self):
    self.killed = True
    
  
  def myprint(self,str):
    self.myprintsignal.emit(str)


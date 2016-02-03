# -*- coding: utf-8 -*-

import math
from time import strftime, gmtime
from PyQt4.QtCore import *

class CATDB(object):
  def __init__(self, obj):
    self.parent = obj
    self.cat_list = {}
    
  def add_cat(self, cat, x, y, name):
    if not cat in self.cat_list:
      self.cat_list[cat]= (x, y, name)
#      self.myprint("add_cat " + str(cat) + " "+ str(x) + " " + str(y))

  def get_cat(self, x0, y0, dist):
    res = {}
    
    for k,v in self.cat_list.items():
      d = math.sqrt((v[0] - x0)**2 + (v[1] - y0 )**2)
      if d < dist:
#        self.myprint("get_cat: %d, %f" % (k, d))
        res[k]=d
    #self.myprint(str(res))
    return res

  def get_cat_name(self, cat):
    if cat == -1:
      return QCoreApplication.translate('code', "Origin")
    elif cat == -2:
      return QCoreApplication.translate('code', "Destination")
    elif cat in self.cat_list:
      return self.cat_list[cat][2]
    else: return ""

  def myprint(self,str):
    if self.parent <> None:
      #self.parent.myprint (str)
      buf=''
    else:
      print str




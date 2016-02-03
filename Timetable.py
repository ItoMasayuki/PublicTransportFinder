# -*- coding: utf-8 -*-

from PyQt4.QtCore import *

class TimetableNode:
  def __init__(self,station_id,prev,route_id,time):
    self.prev = prev
    self.next = None
    self.station_id = station_id
    self.route_id = route_id
    self.time=time  # nodeへの到着時刻かつnodeからの出発時刻
    self.adjacent = None
  def add_adjacent(self, node):
    self.adjacent.append(node)

class Timetable:
  def __init__(self,obj):
    self.parent=obj
    self.node_list = []   # nodeのポインタ
    self.transit_list = {}
    self.connection_list = {}
    self.route_list = {}
    
    self.prev = None
    self.route_id = 0
    self.tmptime = 0
  def add_node(self, station_id, prev, route_id, time, route_name):
    new_node = TimetableNode(station_id,prev,route_id,time)
    self.node_list.append(new_node)
    if not route_id in self.route_list:
      self.route_list[route_id]=route_name
    if prev != None:
      prev.next = new_node
    return new_node
  def get_route_name(self, route_id):
    if route_id == -1:
      return QCoreApplication.translate('code', "by walk")
    elif route_id in self.route_list:
      return self.route_list[route_id]
    else:
      return ""
  def find_nodes(self,station_id):
    if station_id == -1 or station_id == -2:
      return [station_id]
    nodes = []
    for node in self.node_list:
      if node.station_id == station_id:
        nodes.append(node)
    return nodes
  # 時刻表を読み込む。時刻表はルートＩＤ、時刻でソート
  # されている前提。
  def add_timetable(self, route_id, cat, time, route_name):
    #self.myprint("add_timetable %d, %d, %f" % (route_id, cat, time))
    if self.route_id <> route_id:
      self.prev=self.add_node(cat, None, route_id, time, route_name)
    else:
      if not cat in self.connection_list:
        self.connection_list[cat]=set([])
      self.connection_list[cat].add(self.prev.station_id)
      if time <> self.tmptime:
        self.prev=self.add_node(cat, self.prev, route_id, time, route_name)
      else:
        self.prev=self.add_node(cat, self.prev, route_id, time+0.000001, route_name)
      self.tmptime = time
    self.route_id=route_id

  def set_transit(self, station_id_a, station_id_b, required_time):
    if not station_id_a in self.transit_list:
      self.transit_list[station_id_a] = {}
    self.transit_list[station_id_a][station_id_b] = required_time
  def printout(self):
    self.myprint ("printout - timetable")
    for node in self.node_list:
      self.myprint (str(node))
      self.myprint ("  station_id " + str(node.station_id ))
      self.myprint ("  route_id " + str(node.route_id))
      self.myprint ("  time " + str(node.time))
      self.myprint ("  prev " + str(node.prev))
      self.myprint ("  next " + str(node.next))
    self.myprint ("")
  def myprint(self,str):
    #self.parent.myprint (str)
    buf=''


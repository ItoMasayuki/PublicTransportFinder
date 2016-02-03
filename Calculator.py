# -*- coding: utf-8 -*-

import time
from time import strftime, gmtime
#from PyQt4.QtCore import *

class Vertex:
  def __init__(self,node,time):
    self.node = node      # 時刻表ノードのポインタ
    self.adjacent = []    # v のポインタ
    self.route_id = -1    # v へ到着した際の経路
    self.time = time      # v への到着時刻
    self.visited = False
    self.previous = None  # v のポインタ
  def add_adjacent(self, v):
    if not v in self.adjacent:
      self.adjacent.append(v)
  def get_station_id(self):
    if self.node == -1 or self.node == -2:
      return self.node
    return self.node.station_id
  def get_route_id(self):
    if self.node == -1 or self.node == -2:
      return -1
    return self.route_id

class Graph:
  def __init__(self,obj,search_direction):
    self.parent=obj
    self.v_list = []
    self.unfixed_list = []
    self.search_direction = search_direction

    if search_direction == 1:
      self.MAX_TIME = 999999
    elif search_direction == 2:
      self.MAX_TIME = -999999

    self.time_found = self.MAX_TIME
    self.cost_list = {}
  def find_vertex(self,node):
    for v in self.v_list:
      if v.node == node:
        return v
    return None
  def get_vertex(self,node):
    v = self.find_vertex(node)
    if v == None:
      v = Vertex(node,self.MAX_TIME)
      self.v_list.append(v)
      self.unfixed_list.append(v)
    return v
  def add_adjacent(self, node, adj):
    v = self.find_vertex(node)
    v.add_adjacent(adj)
    
  def add_vertex(self, node, prev):
    # timeはprevを出発する時刻
    # （不必要に検索範囲を拡大しないための足きり用）
    v = self.get_vertex(node)
    if prev == None:
      return v
    v.add_adjacent(prev)
    prev.add_adjacent(v)
    return v
  def set_time(self, v, prev, route_id, time):
#    if v.get_station_id() == 1057:
#      self.myprint("dbg: %s\n\t%d\t%d\t%d\t%f\t%f\t%s" % \
#        (str(v.node), v.get_station_id(), prev.get_station_id(), route_id, v.time, time, str(self.search_direction == 2 and v.time < time)))

    # timeはvに到着する時刻
    if self.search_direction == 1 and v.time > time:
      v.time = time
      v.route_id = route_id
      v.previous = prev
      if v.node == -2:
        self.time_found = time
    elif self.search_direction == 2 and v.time < time:
      v.time = time
      v.route_id = route_id
      v.previous = prev
      if v.node == -1:
        self.time_found = time
  def set_cost(self, from_station_id, to_station_id, cost):
    #self.myprint("dbg: " + str(self.cost_list))
    if not from_station_id in self.cost_list:
      self.cost_list[from_station_id] = {}
    self.cost_list[from_station_id][to_station_id] = cost
    #self.myprint("dbg: " + str(self.cost_list) + "\n")
  def find_min(self):
    return min(self.unfixed_list, key=lambda x:x.time)
  def find_max(self):
    return max(self.unfixed_list, key=lambda x:x.time)
  def set_visited(self, v):
    v.visited=True
    self.unfixed_list.remove(v)
    
  def printout(self):
    self.myprint ("printout - graph")
    for v in self.v_list:
      d=1
      if d==1:
        self.myprint (str(v))
        self.myprint ("  node " + str(v.node))
        self.myprint ("  time " + str(v.time))
        self.myprint ("  route_id " + str(v.get_route_id()))
        self.myprint ("  station_id " + str(v.get_station_id()))
        self.myprint ("  visited " + str(v.visited))
        self.myprint ("  previous " + str(v.previous))
        self.myprint ("  adjacent")
        for adj in v.adjacent:
          self.myprint ("    " + str(adj))
        self.myprint ("")
      else:
        self.myprint(" station_id:%d route_id:%d time:%f visited:%s\n" \
                     % (v.get_station_id, v.get_route_id, v.time, str(v.visited)))
    self.myprint("\n")

  # 検索結果を表示する
  def print_result(self):
    buf = 'result'
    #buf = QCoreApplication.translate('code','result:')
    
    # ゴールの頂点を探す
    if self.search_direction == 1:
      i = -2
    elif self.search_direction == 2:
      i = -1
    v = self.find_vertex(i)
    while v <> None:
      if v.node==-1:
        lbl = 'start'
#        lbl = QCoreApplication.translate('code','start')
      elif v.node==-2:
        lbl = 'goal'
#        lbl = QCoreApplication.translate('code','goal')
      else:
        lbl = "%d %s %d %s" % (v.get_station_id(), self.parent.cat_db.get_cat_name(v.get_station_id()), v.get_route_id(),self.parent.timetable.get_route_name(v.get_route_id()))
        
      if self.search_direction == 1:
        buf = strftime("%H:%M:%S ",gmtime(v.time*86400+1)) + lbl + "\n" + buf
      elif self.search_direction == 2:
        buf = buf + "\n" +strftime("%H:%M:%S ",gmtime(v.time*86400+1)) + lbl
      v = v.previous
    if buf<>"":
      self.myprint(buf)
    else:
      self.myprint("- path not found")
      self.myprint(" ")

  def print_result2(self):
    buf1 = ''
    buf2=''
    r_tmp = -2
    s_tmp = ''
    
    # ゴールの頂点を探す
    if self.search_direction == 1:    i = -2
    elif self.search_direction == 2:  i = -1
    v = self.find_vertex(i)

    if v <> None:
      buf1 = strftime("%H:%M:%S, ",gmtime(v.time*86400+1))
    else:
      self.myprint(u"経路が見つかりませんでした。")
      return

    while v <> None:
      if r_tmp <> v.get_route_id() or v.previous == None:
        if self.search_direction == 1:
          buf2 = " (%d %s %d %s %s)" % ( \
                        v.get_station_id(), \
                        self.parent.cat_db.get_cat_name(v.get_station_id()), \
                        r_tmp, \
                        self.parent.timetable.get_route_name(r_tmp), \
                        strftime("%H:%M:%S ",gmtime(v.time*86400+1))) + buf2
        elif self.search_direction == 2:
          buf2 = buf2 + " (%d %s %d %s %s)" % ( \
                        v.get_station_id(), \
                        self.parent.cat_db.get_cat_name(v.get_station_id()), \
                        v.get_route_id(), \
                        self.parent.timetable.get_route_name(v.get_route_id()), \
                        strftime("%H:%M:%S ",gmtime(v.time*86400+1)))
      r_tmp = v.get_route_id()

      v = v.previous

    buf = buf1 + buf2
    self.myprint(buf)

  def myprint(self,str):
    self.parent.myprint (str)



class Calculator(object):
  def __init__(self, parent, timetable, cat_db):
    self.parent = parent
    self.timetable = timetable
    self.cat_db = cat_db
    self.reachable_cat = set([])
    self.buf = u''
    self.reachable_visited = set([])
        
  def initialize(self, search_direction):
    self.g = None
    self.g = Graph(self, search_direction)
  
  # 出発点／到着点から特定の駅への移動時間を設定
  # 駅間の乗換時間を設定
  def add_cost(self,from_station_id, to_station_id, cost):
    #self.myprint("add_cost %d, %d, %f" % (from_station_id, to_station_id, cost))
    if self.g.search_direction ==1:
      self.g.set_cost(from_station_id, to_station_id, cost)
    elif self.g.search_direction ==2:
      self.g.set_cost(to_station_id, from_station_id, cost)


  # station_idのリストの各要素に対応する時刻表の頂点番号の
  # リストを返す。timeの範囲外のものは無視する
  #  返り値：station_idのリスト
  def find_timetablenodes(self, sta):
    return self.timetable.find_nodes(sta)

  def find_reachable(self, cat, stack):
    #self.myprint ("find_reachable: %d" % (cat))
    if cat in set([27]):
        self.myprint ("found")
    
    if cat == -2:
      self.reachable_visited.add(cat)
      self.reachable_cat = self.reachable_cat.union(stack)
      return
    
    adj = set([])
    if cat in self.timetable.connection_list:
      adj = adj.union(self.timetable.connection_list[cat])
    if cat in self.timetable.transit_list:
      adj = adj.union(set(self.timetable.transit_list[cat].keys()))
    if cat in self.g.cost_list:
      adj = adj.union(set(self.g.cost_list[cat].keys()))
    
    #self.myprint ("adj:"+ str(adj))
    
    #res = set([])
    for c in adj:
      if not c in self.reachable_visited and not c in stack:
        s = list(stack)
        s.append(c)
        self.find_reachable(c, s)
    for c in adj:
      if c in self.reachable_cat:
        self.reachable_cat = self.reachable_cat.union(stack)
    #if len(res) > 0: res.add(cat)
    
    #self.myprint ("res:"+ str(res))

    self.reachable_visited.add(cat)


  def dijkstra_1(self, start_time):
    # 出発時刻指定の検索
    
    #self.timetable.printout()
    #self.myprint(str(self.timetable.transit_list))
    
    v0 = self.g.get_vertex(-1)
    v0.time = start_time
    sta_time = {}

    counter = 0

    #self.myprint(str(self.g.cost_list))

    # 処理対象のノードがある限り繰り返す
    while( len(self.g.unfixed_list)!=0 ):
      # 未訪問で重みが十分大きくないノードの中で一番重みが小さい
      # 頂点を処理対象のノードとします。
      v = self.g.find_min()
      if v==None:
        break
        
      if v.node != -1 and v.node!=-2 and v.node.next!=None:
        # 時刻表通りに進む場合
        if v.time <= v.node.time and v.node.next.time <= self.g.time_found:
          vn = self.g.add_vertex(v.node.next, v)
          if vn != None:
            self.g.set_time(vn, v, v.node.route_id, v.node.next.time)

      if v.get_station_id() in self.timetable.transit_list:
        # 乗換表に値がある場合
        stas = self.timetable.transit_list[v.get_station_id()].keys()
        for sta in stas:
          if not sta in sta_time or v.time < sta_time[sta]:
            for node in self.timetable.find_nodes(sta):
              if v.time < node.time and node.time < self.g.time_found:
                vn = self.g.add_vertex(node, v)
                if vn != None:
                  self.g.set_time(vn, v, -1, v.time + self.timetable.transit_list[v.get_station_id()][sta])
            sta_time[sta]=v.time

      if v.get_station_id() in self.g.cost_list:
        stas = self.g.cost_list[v.get_station_id()].keys()
        for sta in stas:
          for node in self.timetable.find_nodes(sta):
            if node ==-2 or node == -1 or v.time < node.time and node.time < self.g.time_found:
              vn = self.g.add_vertex(node, v)
              if vn != None:
                self.g.set_time(vn, v, -1, v.time + self.g.cost_list[v.get_station_id()][sta])

      self.g.set_visited(v)

      #self.myprint("in progress")
      #self.g.printout()
      counter = counter + 1
      if counter > 100:
        counter = 0

    self.g.print_result2()

  def dijkstra_2(self, arriv_time):
    # 到着時刻指定の検索
    
    #self.timetable.printout()
    #self.myprint(str(self.timetable.transit_list))
    
    v0 = self.g.get_vertex(-2)
    v0.time = arriv_time
    sta_time = {}
    
    counter = 0

    #self.myprint(str(self.g.cost_list))

    # 処理対象のノードがある限り繰り返す
    while( len(self.g.unfixed_list)!=0 ):
      # 未訪問で重みが十分大きくないノードの中で一番重みが小さい
      # 頂点を処理対象のノードとします。
      v = self.g.find_max()
      #self.myprint("dbg: " + str(v.node))
      if v==None:
        break
    
      if v.get_station_id() == 976 or v.get_station_id == 99018: 
        debug=""
        
      if v.node != -1 and v.node!=-2 and v.node.prev!=None:
        # 時刻表通りに進む場合
        if v.time >= v.node.time \
            and v.node.prev.time >= self.g.time_found:
#            and v.get_station_id() in self.reachable_cat:
          vn = self.g.add_vertex(v.node.prev, v)
          if vn != None:
            self.g.set_time(vn, v, v.node.route_id, v.node.prev.time)

      if v.get_station_id() in self.timetable.transit_list:
        # 乗換表に値がある場合
        stas = self.timetable.transit_list[v.get_station_id()].keys()
        for sta in stas:
          if not sta in sta_time or sta_time[sta]<v.time:
            for node in self.timetable.find_nodes(sta):
              if v.time > node.time and node.time > self.g.time_found:
#                if node.station_id in self.reachable_cat:
                  vn = self.g.add_vertex(node, v)
                  if vn != None:
                    self.g.set_time(vn, v, -1, v.time - self.timetable.transit_list[v.get_station_id()][sta])
            sta_time[sta]=v.time

      if v.get_station_id() in self.g.cost_list:
        stas = self.g.cost_list[v.get_station_id()].keys()
        for sta in stas:
#          if sta in self.reachable_cat:
            for node in self.timetable.find_nodes(sta):
              if node ==-1 or node == -2 or v.time > node.time and node.time > self.g.time_found:
                vn = self.g.add_vertex(node, v)
                if vn != None:
                  self.g.set_time(vn, v, -1, v.time - self.g.cost_list[v.get_station_id()][sta])

      self.g.set_visited(v)

      #self.myprint("in progress")
      #self.g.printout()

      counter = counter + 1
      if counter > 100:
        counter = 0
    self.g.print_result2()
    
  def run(self,start_time):
    #self.myprint("SD %d" % self.g.search_direction)
    
    start = time.time()
    
#    self.find_reachable(-1, [-1])

    #self.reachable_cat =self.timetable.connection_list.keys()
    #self.myprint ("find reachable:" + str(self.reachable_cat))
    #self.myprint ("connection list:" + str(self.timetable.connection_list))
    #self.myprint ("cost list:" + str(self.g.cost_list))
    
    if self.g.search_direction == 1:
      self.dijkstra_1(start_time)
    elif self.g.search_direction == 2:
      self.dijkstra_2(start_time)
    elapsed_time = time.time() - start
    #self.myprint (QCoreApplication.translate('code','elapsed time:')\
    #  + "{0}".format(elapsed_time) + "[sec]\n")
    #self.myprint ('elapsed time:' + "{0}".format(elapsed_time) + "[sec]\n")
    return self.buf

  def myprint(self,str):
    if self.parent <> None:
      #self.parent.myprint (str)
      self.buf = self.buf + str
    else:
      print str




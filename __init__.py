# -*- coding: UTF-8 -*-

#import os,sys
#sys.path.append(r"C:\Users\ito\.p2\pool\plugins\org.python.pydev_4.5.0.201601121553\pysrc")
#import pydevd
#pydevd.settrace()

def classFactory(iface):
    from PublicTransportFinder import PublicTransportFinder

    return PublicTransportFinder(iface)

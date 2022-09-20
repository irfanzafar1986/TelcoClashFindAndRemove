# -*- coding: utf-8 -*-
"""
Created on Sat Sep 10 05:27:57 2022

@author: m_irf
"""
"""
Created on Tue Feb  8 11:13:36 2022

@author: m_irf
"""
class Cell_3g:
    def __init__(self, site, cid,lat,long,sc,band,azimuth):
        self.site = site
        self.cid = cid
        self.lat=lat
        self.long=long
        self.sc=sc
        self.band=band
        self.azimuth=azimuth
   
    def isScClash(self,cellB):
        ''' Returns if there is BCCH clash between two cells or not
        It is assumed that different band cells will not reach till this stage'''
        if(self.sc==cellB.sc):
            return True
        return False
    def toList(self):
        return [int(self.cid),int(self.sc),0],['cell','sc','dummy']
    def set_param(self,param_name,value):
        if param_name=='sc':
            self.sc=value
      
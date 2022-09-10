"""
Created on Tue Feb  8 11:13:36 2022

@author: m_irf
"""
from geopy.distance import geodesic
import math
class Cell_2g:
    def __init__(self, site, cid,lat,long,bcch,band,azimuth,bsic):
        self.site = site
        self.cid = cid
        self.lat=lat
        self.long=long
        self.bcch=bcch
        self.bsic=bsic
        self.band=band
        self.azimuth=azimuth
   
    def isBcchClash(self,cellB):
        ''' Returns if there is BCCH clash between two cells or not
        It is assumed that different band cells will not reach till this stage'''
        if(self.bcch==cellB.bcch):
            return True
        return False
    def isBcchBsicClash(self,cellB):
        ''' Returns if there is BCCH BSIC clash between two cells or not 
        It is assumed that different band cells will not reach till this stage'''
        if (self.bcch==cellB.bcch and self.bsic==cellB.bsic):
            return True
        return False       
    def isAdjBcch(self,cellB):  
        ''' Returns if there is BCCH is adjcacnet between two cells or not 
        It is assumed that different band cells will not reach till this stage'''
        diff=abs(self.bcch-cellB.bcch)
        if (diff<=1):
            return True
        return False       
    
      
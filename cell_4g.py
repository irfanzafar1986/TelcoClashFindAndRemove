# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 14:48:27 2022

@author: m_irf
"""
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 10 05:27:57 2022

@author: m_irf
"""
"""
Created on Tue Feb  8 11:13:36 2022

@author: m_irf
"""
class Cell_4g:
    ncs_config=dict()
    ncs_config[1]=(1,0.76)
    ncs_config[2]=(2,1.04)
    ncs_config[3]=(2,1.47)
    ncs_config[4]=(2,2.04)
    ncs_config[5]=(2,2.62)
    ncs_config[6]=(3,3.48)
    ncs_config[7]=(3,4.33)
    ncs_config[8]=(4,5.48)
    ncs_config[9]=(5,7.34)
    ncs_config[10]=(6,9.77)
    ncs_config[11]=(8,12.2)
    ncs_config[12]=(10,15.92)
    ncs_config[13]=(13,22.78)
    ncs_config[14]=(22,38.8)
    ncs_config[15]=(32,58.83)
    ncs_config[0]=(64,118.9)
    
    def __init__(self, site, cid,lat,long,band,rsi,ncs,pci,azimuth):
        self.site = site
        self.cid = cid
        self.lat=lat
        self.long=long
        self.band=band
        self.rsi=rsi
        self.ncs=ncs
        self.pci=pci
        self.azimuth=azimuth
    def isPciClash(self,cellB):
        return self.pci==cellB.pci
    def isRsi_Clash(self,cellB):
        ''' Returns if there is clash between two cells or not
        max_allowed_tier is the maximum tier to check '''
        s1=self.rsi
        e1=s1+Cell_4g.ncs_config[self.ncs][0]-1
        s2=cellB.rsi
        e2=s2+Cell_4g.ncs_config[cellB.ncs][0]-1
        if (e1>=s2 and e1<e2) or (s1>=s2 and s1<e2) or (e2>=s1 and e2<e1) or (s2>=s1 and s2<e1):
            return True
        return False
    def toList(self):
        return [self.cid,int(self.rsi),int(self.pci)],['cell','rsi','pci']
    
    def set_param(self,param_name,value):
        if param_name=='rsi':
            self.rsi=value
        if param_name=='pci':
            self.pci=value
        if param_name=='ncs':
            self.ncs=value  
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 17:09:09 2022

@author: m_irf
"""



def get_tier(dict_for_tier):
    ''' Takes a dictionary of current quads and appends tier in value'''
    key=[]
    val=[]    
    for i in range(6):# we have 6 quads
        curr_quad_dict={k: v for k, v in dict_for_tier.items() if v[2]==i} # filter dictionary for current quad
        curr_quad_tier=sorted(curr_quad_dict.items(),key=lambda kv:kv[1][0])[:10]# Get first 10 tiers 
        for i,item in enumerate(curr_quad_tier):
            key.append(item[0]) # Append current site as key
            val.append((item[1][0],item[1][1],i)) # Append current values
    return dict(zip(key,val))
def make_site_tiers(index):
    from geopy.distance import geodesic
    import math
    import pandas as pd
    import pickle

    site_total=pd.read_csv("D:/Office backup/tools/python/rsi clash/Sites-2022-08-29.csv")
    site_count=len(site_total)
    start=index*site_count//6
    end=site_count-((5-index)*site_count//6)
    site_df1=site_total.iloc[start:end]
    dist_angle_tier_dict={}
    for i,site1 in site_df1.iterrows():
        dict_for_tier={}
        for j,site2 in site_total.iterrows(): 
            if(site1.site==site2.site):
                continue
            dist=geodesic((site1.Latitude, site1.Longitude), (site2.Latitude, site2.Longitude)).meters
            if(dist<20000):# skip sites more than 20 KM away take this distance from user in production envoirment
                angle=(math.atan2(site2.Longitude - site1.Longitude, site2.Latitude - site1.Latitude)*180/math.pi+360)%360
                quad=math.floor(angle/60)
                dict_for_tier[site2.site]=(dist,angle,quad)# Add current site in temporary dictionary
        dist_angle_tier_dict[site1.site]=get_tier(dict_for_tier) # Calculate tiers of the site once we have tiers we can filter them easily
    pickle.dump(dist_angle_tier_dict,open(f"final_dict_part{index}",'wb'))
        
        

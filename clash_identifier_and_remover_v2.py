# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 14:40:03 2022

@author: m_irf
"""
import pickle
import pandas as pd
import gpxpy.geo as geo
import numpy as np
import math
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
from cells.Cell_2g import Cell_2g
import io
from PIL import Image
from cells.Cell_3g import Cell_3g
from cells.cell_4g import Cell_4g
import random

####################################################################################################3
st.title("Planning Parameters Clashes- Identifier and Remover")
input_file=st.file_uploader("Please Select Cell list with columns shown below",type=".csv")
plan_input_file=st.file_uploader("Please Select Cell list For cells you want to plan",type=".csv")
match_dict={}

### Match dict will be used to map GUI Values to the one passed in functions
match_dict['2G- BCCH/BSIC Clash']='bcch_bsic'
match_dict['2G BCCH Clash']='bcch'
match_dict['3G Scrambling Code clash']='sc'
match_dict['LTE-PCI Clash ']='pci'
match_dict['LTE Rsi Clash']='rsi'
### Plan Match dict will be used to map GUI Values to the one passed in functions
### Also ranges per param are defined separately based on current project 

plan_match_dict={}
plan_match_dict['Plan BCCH']=('bcch',[i for i in range(1,5)]+[j for j in range(40,49)]) # May change as per need
plan_match_dict['Plan BSIC']=('bsic',[n*10+b for b in range(7) for n in range(7)]) # Fixed by 3GPP 
plan_match_dict['Plan SC']=('sc', [i for i in range(1,512)]) # # Fixed by 3GPP
plan_match_dict['Plan PCI']=('pci',[i for i in range(1,504)])# Fixed by 3GPP
plan_match_dict['Plan RSI']=('rsi',[i for i in range(1,837)])# Fixed by 3GPP


## This dict to be created using separate process after update of physical data
site_dict={}
for i in range(6): ## We created 6 processes
    file = open(f"D:/Office backup/tools/python/rsi clash/final_dict_part{i}", 'rb')
    site_dict={**site_dict ,** pickle.load(file)}
    
## Start StreamLit design    
st.sidebar.title("Options")    
add_radio = st.sidebar.radio(
        "Choose Which Incosistency you would like to find",
        ("2G- BCCH/BSIC Clash", "2G BCCH Clash", "3G Scrambling Code clash",
          "LTE-PCI Clash ", "LTE Rsi Clash", "Plan BCCH","Plan BSIC","Plan SC","Plan PCI","Plan RSI"))
user_max_tier = st.sidebar.slider('Please select max tier for clash search?', 0, 10, 5)

if(add_radio =="2G- BCCH/BSIC Clash" or add_radio=="2G BCCH Clash" or add_radio=="Plan BCCH" or add_radio=="Plan BSIC"):    
   # For 2G make cell list of 2G
   cell_list=[]
   if(input_file is not None):
       cell_data=pd.read_csv(input_file)
       for i,rows in cell_data.iterrows():
           c=Cell_2g(rows.site, rows.cell,rows.Latitude,rows.Longitude,rows.BCCH,rows.Band,rows.Azimuth,rows.BSIC)
           cell_list.append(c)
   if(add_radio=="Plan BCCH" or add_radio=="Plan BSIC"):    
       #For Plan make cell list of plan also
       plan_cell_list=[]
       if(plan_input_file is not None):
           plan_cell_data=pd.read_csv(plan_input_file)
           for i,rows in plan_cell_data.iterrows():
                plan_c=Cell_2g(rows.site, rows.cell,rows.Latitude,rows.Longitude,rows.BCCH,rows.Band,rows.Azimuth,rows.BSIC)
                plan_cell_list.append(plan_c)
   image = Image.open('D:/Office backup/tools/python/rsi clash/Cell_file_picture.png')
if(add_radio =="3G Scrambling Code clash" or add_radio =="Plan SC" ):    
   cell_list=[]
   if(input_file is not None):
       cell_data=pd.read_csv(input_file)
       for i,rows in cell_data.iterrows():
           c=Cell_3g(rows.site, rows.cell,rows.Latitude,rows.Longitude,rows.scr,rows.band,rows.Azimuth)
           cell_list.append(c)
   if(add_radio=="Plan SC"):    
       plan_cell_list=[]
       if(plan_input_file is not None):
           plan_cell_data=pd.read_csv(plan_input_file)
           for i,rows in plan_cell_data.iterrows():
               plan_c=Cell_3g(rows.site, rows.cell,rows.Latitude,rows.Longitude,rows.scr,rows.band,rows.Azimuth)
               plan_cell_list.append(plan_c)
image = Image.open('D:/Office backup/tools/python/rsi clash/Cell_file_picture-3g.png')
if(add_radio =="LTE-PCI Clash " or add_radio=="LTE Rsi Clash" or add_radio =="Plan PCI" or add_radio =="Plan RSI" ):    
   cell_list=[]
   if(input_file is not None):
       cell_data=pd.read_csv(input_file)
       for i,rows in cell_data.iterrows():
           c=Cell_4g(rows.site, rows.cell,rows.Latitude,rows.Longitude,rows.band,rows.rsi,rows.ncs,rows.pci,rows.Azimuth)
           cell_list.append(c)
   if(add_radio =="Plan PCI" or add_radio =="Plan RSI"):    
       plan_cell_list=[]
       if(plan_input_file is not None):
           plan_cell_data=pd.read_csv(plan_input_file)
           for i,rows in plan_cell_data.iterrows():
                plan_c=Cell_4g(rows.site, rows.cell,rows.Latitude,rows.Longitude,rows.band,rows.rsi,rows.ncs,rows.pci,rows.Azimuth)
                plan_cell_list.append(plan_c)
   image = Image.open('D:/Office backup/tools/python/rsi clash/Cell_file_picture-4g.png')
st.image(image)

lock = st.sidebar.checkbox('Lock Settings') # Streamlit has a problem it starts running after any change this is to avoid that problem (19 Sep 2022)

def action_button():
    if (lock):
        get_clash(match_dict.get(add_radio,0))
        plan(plan_match_dict.get(add_radio,0))
def get_clash(clash_type):
    if clash_type==0:
        return 
    ### Finds clash in the network based on clash type enterned 
    ###clash type should be 'bcch','bcch_bsic','sc','pci','rsi
    result=[]
    for cell in cell_list:
        candid_cell_list=generate_candid_cell_list(cell,site_dict,user_max_tier)
        if(clash_type=='bcch'):
            curr_clashes=[res for res in candid_cell_list if(cell.isBcchClash(res))]
        if(clash_type=='bcch_bsic'):
            curr_clashes=[res for res in candid_cell_list if(cell.isBcchBsicClash(res))]
        if(clash_type=='sc'):
            curr_clashes=[res for res in candid_cell_list if(cell.isScClash(res))]
        if(clash_type=='rsi'):
            candid_cell_list=[a for a in candid_cell_list if a.band==cell.band]
            curr_clashes=[res for res in candid_cell_list if(cell.isRsi_Clash(res))]
        if(clash_type=='pci'):
            candid_cell_list=[a for a in candid_cell_list if a.band==cell.band]
            curr_clashes=[res for res in candid_cell_list if(cell.isPciClash(res))]
        for clashed_cell in curr_clashes:
            site_site_rel=site_dict[str(int(cell.site))][str(int(clashed_cell.site))]
            angle1=site_site_rel[1]-cell.azimuth
            angle2=180+site_site_rel[1]-clashed_cell.azimuth
            adj=math.cos(np.radians(angle1))+math.cos(np.radians(angle2))
            prio=2+site_site_rel[2]-adj
            if(prio<=user_max_tier):
                temp=cell.toList()+[clashed_cell.cid]+[site_site_rel[0]]+[prio]
                result.append(temp)
    result_df=pd.DataFrame(result,columns=('cell1','param1','param2','cell2','dist','prio'))         
    result_df.sort_values(by='prio',inplace=True)
    st.dataframe(result_df)#.style.format("{:.0f}"))
    result_df.to_csv(f"results/{clash_type}/{clash_type}_clash.csv",index=False)
    show_top(result_df) 
    save_htmls(result_df,clash_type)

def plan(plan_type):
    if plan_type==0:
        return 
    range_param=plan_type[1]
    # Plans param for cell in the network based on plan type enterned 
    # clash type should be 'bcch','bsic','sc','pci','rsi'''
    plan_result=[]
    for cell in plan_cell_list:
        if(plan_type[0]=='bcch'):   
            orig=cell.bcch
        if(plan_type[0]=='bsic'):   
            orig=cell.bsic
        if(plan_type[0]=='sc'):   
            orig=cell.sc
        if(plan_type[0]=='rsi'):   
            orig=cell.rsi
        if(plan_type[0]=='pci'): 
            orig=cell.pci
        plan_candid_cell_list=generate_candid_cell_list(cell,site_dict,user_max_tier)
        plan_candid_cell_list=[a for a in plan_candid_cell_list if a.band==cell.band]
        random.shuffle(range_param)
        for curr in range_param :
            count=0
            if(plan_type[0]=='bcch'):   
                cell.bcch=curr
                curr_clashes=[res for res in plan_candid_cell_list if(cell.isBcchClash(res))]
                
            if(plan_type[0]=='bsic'):   
                cell.bsic=curr
                curr_clashes=[res for res in plan_candid_cell_list if(cell.isBcchBsicClash(res))]
                
            if(plan_type[0]=='sc'):   
                cell.sc=curr
                curr_clashes=[res for res in plan_candid_cell_list if(cell.isScClash(res))]
            
            if(plan_type[0]=='rsi'):   
                cell.rsi=curr
                plan_candid_cell_list=[a for a in plan_candid_cell_list if a.band==cell.band]
                curr_clashes=[res for res in plan_candid_cell_list if(cell.isRsi_Clash(res))]
            if(plan_type[0]=='pci'):   
                cell.pci=curr
                plan_candid_cell_list=[a for a in plan_candid_cell_list if a.band==cell.band]
                curr_clashes=[res for res in plan_candid_cell_list if(cell.isPciClash(res))]
            if len(curr_clashes)==0:
                new_cell=update_in_celllist(cell, cell_list,curr,plan_type[0])
                new_cell_values,headers=new_cell.toList()
                plan_result.append(new_cell_values+[orig])
                break
            for clashed_cell in curr_clashes:
                site_site_rel=site_dict[str(int(cell.site))][str(int(clashed_cell.site))]
                angle1=site_site_rel[1]-cell.azimuth
                angle2=180+site_site_rel[1]-clashed_cell.azimuth
                adj=math.cos(np.radians(angle1))+math.cos(np.radians(angle2))
                prio=site_site_rel[2]-adj+2
                if(prio<=user_max_tier):
                    count+=1
                    break
            if count==0:
                new_cell=update_in_celllist(cell, cell_list,curr,plan_type[0])
                new_cell_values,headers=new_cell.toList()
                plan_result.append(new_cell_values+[orig])
                break
    st.success(f"Following are new {plan_type[0]}")        
    result_df=pd.DataFrame(plan_result,columns=['cell',f"New {headers[1]}",f"New {headers[2]}",f"Pre {plan_type[0]}"])
    result_df.to_csv(f"results/{plan_type[0]}/planned_{plan_type[0]}.csv",index=False)
    st.dataframe(result_df)
    
def update_in_celllist(orig_cell,cell_list,new_value,param):
     index=get_cell_index(orig_cell.cid,cell_list)
     cell_list.pop(index)
     new_cell=orig_cell
     new_cell.set_param(param,new_value)
     cell_list.append(new_cell)
     return new_cell
 
def show_top(df):
    ''' This function shows first clash  on map and displays dataframe'''
    try: # Using Try bcz different tech cells have different types
        src=int(df.iloc[0]['cell1'])
        tgt=int(df.iloc[0]['cell2'])
    except:
        src=df.iloc[0]['cell1']
        tgt=df.iloc[0]['cell2']
    
    loc1=get_loc(src)
    loc2=get_loc(tgt)
    st.write(f"For example check below clash , All Calshes picutres are stored in corresponding folder")
    m=show_cells(cell_data,loc1[0],loc1[1],src,loc1[2],loc2[0],loc2[1],tgt,loc2[2])
    folium_static(m)
def save_htmls(df,fldr):
    ''' Stores html for all clashes passed in df '''
    for i, rows in df.iterrows():
        try:
            src=int(rows['cell1'])
            tgt=int(rows['cell2'])
        except:
            src=rows['cell1']
            tgt=rows['cell2']
        
        loc1=get_loc(src)
        loc2=get_loc(tgt)
        m=show_cells(cell_data,loc1[0],loc1[1],src,loc1[2],loc2[0],loc2[1],tgt,loc2[2])
        m.save(f"results/{fldr}/{src}-{tgt}.html")
def get_loc(cell):
    return cell_data[cell_data['cell']==cell][['Latitude','Longitude','Azimuth']].iloc[0]
def generate_candid_cell_list(cella,site_dict,tier=5):
    '''  returns cell list for cella with in allowed tier'''
    curr_site=cella.site
    candid_sites=site_dict[str(int(curr_site))] # take sites from dictionary
    all_sites=dict(filter(lambda x: x[1][2]<=tier, candid_sites.items())) # take sites within check tier
    return [cell for cell in cell_list if str(int(cell.site)) in all_sites]

def show_nw(nw,long,lat):
    m = folium.Map(location=[lat,long],zoom_start=15)
    length = .002 
    for i,row in nw.iterrows():
        angle = row.Azimuth
        tooltip = str(row.site)+"_"+str(row.cell)
        origin_point = [row.Latitude, row.Longitude]
        end_lat = origin_point[0] + length * math.cos(math.radians(angle))
        end_lon = origin_point[1] + length * math.sin(math.radians(angle))
        folium.PolyLine([origin_point, [end_lat, end_lon]],color="#000000",tootip=tooltip,popup=tooltip).add_to(m)
    return m
def show_cells(nw,lat,long,cell_name,azi,lat2,long2,cell_name2,azi2):
    ''' Displays cells on folium map, cells passed here will be highlihted above the nw'''
    m = show_nw(nw,long,lat)
    folium.Marker([lat, long], popup=cell_name).add_to(m)
    tooltip = cell_name
    origin_point = [lat, long]
    origin_point2=[lat2,long2]
    length = .002
    angle = azi
    angle2=azi2
    end_lat = origin_point[0] + length * math.cos(math.radians(angle))
    end_lon = origin_point[1] + length * math.sin(math.radians(angle))
    end_lat2 = origin_point2[0] + length * math.cos(math.radians(angle2))
    end_lon2= origin_point2[1] + length * math.sin(math.radians(angle2))
    folium.PolyLine([origin_point, [end_lat, end_lon]],weight=10,color="red").add_to(m)
    folium.PolyLine([origin_point2, [end_lat2, end_lon2]],weight=10,color="red").add_to(m)
    return m
def get_cell_index(cell,nw_cells):
    for i, e in enumerate(nw_cells):
        if e.cid == cell:
            return i
st.sidebar.button("Run",  on_click=action_button())
   

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

def get_bcch_bsic_clash():
    result=[]
    for cell in cell_list:
        candid_cell_list=generate_candid_cell_list(cell,site_dict,user_max_tier)
        curr_clashes=[res for res in candid_cell_list if(cell.isBcchBsicClash(res))]
        # Adjust tiering
        for clashed_cell in curr_clashes:
            site_site_rel=site_dict[str(int(cell.site))][str(int(clashed_cell.site))]
            angle1=site_site_rel[1]-cell.azimuth
            angle2=180+site_site_rel[1]-clashed_cell.azimuth
            adj=math.cos(np.radians(angle1))+math.cos(np.radians(angle2))
            prio=2+site_site_rel[2]-adj
            if(prio<=user_max_tier):
                result.append([cell.cid,cell.bcch,cell.bsic,clashed_cell.cid,site_site_rel[0],prio])
    result_df=pd.DataFrame(result,columns=('cell1','bcch','bsic','cell2','dist','prio'))   
    result_df.sort_values(by='prio',inplace=True)
    st.dataframe(result_df.style.format("{:.0f}"))
    show_top(result_df) 
    save_htmls(result_df,"bcch_bsic_clash")
def get_bcch_clash():
    result=[]
    for cell in cell_list:
        candid_cell_list=generate_candid_cell_list(cell,site_dict,user_max_tier)
        curr_clashes=[res for res in candid_cell_list if(cell.isBcchClash(res))]
        # Adjust tiering
        for clashed_cell in curr_clashes:
            site_site_rel=site_dict[str(int(cell.site))][str(int(clashed_cell.site))]
            angle1=site_site_rel[1]-cell.azimuth
            angle2=180+site_site_rel[1]-clashed_cell.azimuth
            adj=math.cos(np.radians(angle1))+math.cos(np.radians(angle2))
            prio=site_site_rel[2]-adj+2
            if(prio<=user_max_tier):
                result.append([cell.cid,cell.bcch,clashed_cell.cid,site_site_rel[0],prio])
    result_df=pd.DataFrame(result,columns=('cell1','bcch','cell2','dist','prio'))   
    result_df.sort_values(by='prio',inplace=True)
    result_df.to_csv("bcch_clash/bcch_clash.csv",index=False,)
    st.dataframe(result_df.style.format("{:.0f}"))    #.to_csv('BCCH_BSIC Clash.csv',index=False)
    show_top(result_df)
    save_htmls(result_df,"bcch_clash")
def show_top(df):
    src=int(df.iloc[0]['cell1'])
    tgt=int(df.iloc[0]['cell2'])
    loc1=get_loc(src)
    loc2=get_loc(tgt)
    st.write(f"For example check below clash , All Calshes picutres are stored in corresponding folder")
    m=show_cells(cell_data,loc1[0],loc1[1],src,loc1[2],loc2[0],loc2[1],tgt,loc2[2])
    folium_static(m)
def save_htmls(df,fldr):
    ''' Stores html for all clashes passed in df '''
    for i, rows in df.iterrows():
        src=int(rows['cell1'])
        tgt=int(rows['cell2'])
        loc1=get_loc(src)
        loc2=get_loc(tgt)
        m=show_cells(cell_data,loc1[0],loc1[1],src,loc1[2],loc2[0],loc2[1],tgt,loc2[2])
        m.save(f"{fldr}/{src}-{tgt}.html")
def store_pic(m,name):
    img_data = m._to_png(5)
    img = Image.open(io.BytesIO(img_data))
    img.save(f'{name}.png')
def get_loc(cell):
    return cell_data[cell_data['cell']==cell][['Latitude','Longitude','Azimuth']].iloc[0]
def generate_candid_cell_list(cella,site_dict,tier=5):
    '''  returns cell list for cella with in allowed tier'''
    curr_site=cella.site
    candid_sites=site_dict[str(int(curr_site))] # take sites from dictionary
    all_sites=dict(filter(lambda x: x[1][2]<=tier, candid_sites.items())) # take sites within check tier
    return [cell for cell in cell_list if str(int(cell.site)) in all_sites]

def action_button():
    if(add_radio=="2G- BCCH/BSIC Clash"):
        get_bcch_bsic_clash()
    if(add_radio=="2G BCCH Clash"):
        get_bcch_clash()
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
image = Image.open('D:/Office backup/tools/python/rsi clash/Cell_file_picture.png')
st.title("Clash Identfier and Remover")
input_file=st.file_uploader("Please Select Cell list with columns shown below",type=".csv")
cell_list=[]
if(input_file is not None):
    cell_data=pd.read_csv(input_file)
    for i,rows in cell_data.iterrows():
        c=Cell_2g(rows.site, rows.cell,rows.Latitude,rows.Longitude,rows.BCCH,rows.Band,rows.Azimuth,rows.BSIC)
        cell_list.append(c)
st.image(image)
site_dict={}
for i in range(6): ## We created 6 processes
    file = open(f"D:/Office backup/tools/python/rsi clash/final_dict_part{i}", 'rb')
    site_dict={**site_dict ,** pickle.load(file)}
st.sidebar.title("Options")    
add_radio = st.sidebar.radio(
        "Choose Which Incosistency you would like to find",
        ("2G- BCCH/BSIC Clash", "2G BCCH Clash", "3G Scrambling Code clash",
          "LTE-PCI ", "LTE Rsi Clash"))
user_max_tier = st.sidebar.slider('Please select max tier for clash search?', 0, 10, 5)
st.sidebar.button("Run",  on_click=action_button())

   

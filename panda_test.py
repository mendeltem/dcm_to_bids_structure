#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 14:52:37 2020

@author: temuuleu
"""


import pandas as pd



import matplotlib.pyplot as plt






proscis_path = "/home/temuuleu/PROSCIS/CSB/S-PROSCIS_MRT/persDaten/query_results_delineation_20200819.xlsx"


df_query = pd.read_excel(proscis_path)


type(df_query)


data = df_query.loc[df_query["ID"]==1000001]



        selected_data = df_query.loc[(data["colorimages"] == color) &
                                 (data["imageid"] == int(imageid))&
                                 (data["masktype"]    == masktype) &
                                 (data["maskregion"]  == maskregion) 
                         ,
                         :]
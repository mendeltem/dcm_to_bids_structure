#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 14:33:47 2020

@author: temuuleu
"""

import os
#import random
import re
import os.path
#import optparse
#import yaml
import pydicom
import openpyxl
import numpy as np
from openpyxl import Workbook
import string
import datetime as dt   
import pandas as pd
import math

def myprint(dataset, indent=0):
    """Go through all items in the dataset and print them with custom format

    Modelled after Dataset._pretty_str()
    """
    dont_print = ['Pixel Data', 'File Meta Information Version']

    indent_string = "   " * indent
    next_indent_string = "   " * (indent + 1)

    for data_element in dataset:
        if data_element.VR == "SQ":   # a sequence
            print(indent_string, data_element.name)
            for sequence_item in data_element.value:
                myprint(sequence_item, indent + 1)
                print(next_indent_string + "---------")
        else:
            if data_element.name in dont_print:
                print("""<item not printed -- in the "don't print" list>""")
            else:
                repr_value = repr(data_element.value)
                if len(repr_value) > 50:
                    repr_value = repr_value[:50] + "..."
                print("{0:s} {1:s} = {2:s}".format(indent_string,
                                                   data_element.name,
                                                   repr_value))
  
def isNaN(num):
    return num != num
              
                
def replace_typeofmri_name(text, key ,replacer):

    if key in text.lower():
        return text.replace(re.search("[a-zA-Z_0-9]*", text)[0], replacer)
    else:
        return text
                
def date_string_slipp(file_directory):
    """convert datename with text to a name without text """
    
    pattern =  "[0-9]*"
                    
    date = re.findall(pattern,file_directory)

    new_date = ""
    first = 0;
    
    for index_date, d in enumerate(date):
        if d and first==0:
            new_date=str(d)
            first = 1;
        elif d:
            new_date+=str(d)
            
    return new_date


def is_file(path_name):
    """check if the given string is a file"""
    if re.search("\.[a-zA-Z]+$", os.path.basename(path_name)):
        return True
    else:
        return False
    
    
def is_directory(path_name):
    """check if the given string is a directory"""
    if not is_file(path_name):
        return True
    else:
        return False
    
    
def create_dir(output_path):
    """creates a directory of the given path"""
    if not os.path.exists(output_path) and is_directory(output_path):
        os.makedirs(output_path)


 
def path_converter(text_path):
    """Convert a path with a space into space with backslash"""

    out = ''
    out_list = []

    for i, t in enumerate(text_path):
        
        if t == ' ':
            out_list.append('\\ ')
        elif t == "(" :
            out_list.append('\(')
        elif t == ")" :
            out_list.append('\)')   
        else:
            out_list.append(t)
        
    return out.join(out_list)



def remove_first_digits(text_path):
    """Convert a path with a space into space with backslash"""

    out = ''

    for i, t in enumerate(text_path):
        
        if t == '_':
            out = text_path[i+1:]
            break
 
    return out


def get_feature_paths(start_dir, extensions = ['dcm']):
    """Returns all image paths with the given extensions in the directory.
    Arguments:
        start_dir: directory the search starts from.
        extensions: extensions of image file to be recognized.
    Returns:
        a sorted list of all image paths starting from the root of the file
        system.
    """
    if start_dir is None:
        start_dir = os.getcwd()
    img_paths = []
    for roots,dirs,files in os.walk(start_dir):
        for name in files:
            for e in extensions:
                if name.endswith('.' + e):
                    img_paths.append(roots + '/' + name)
    img_paths.sort()
    return img_paths

def get_nummeric_only(text):
    """Get only nummer from the string """

    nummeric_string =""
    
    for character in text:
        if character.isnumeric():
           
            nummeric_string+=character
            
    return nummeric_string   

                                
def delete_first_zeros(digit_with_zeros):     
    """Deleting the first zeros from string """       
                
    digit_without_zeros = ""

    snap = 1
    
    d = 0

    for d in digit_with_zeros:

        if d != "0":
            snap = 0
        if snap == 0:
            digit_without_zeros +=d
            
    return digit_without_zeros
                        

def convert_date(date):
    """converting given date structur to datetime
    Arguments:
        date: a string with date and time in it
        
        date = '201004131854'
        
    Returns:
        datetime: datetime  
        
        datetime.datetime(2010, 4, 13, 18, 54)

    """
    date = get_nummeric_only(date)    
    
    
    if len(date) == 8:

        year     =  int(date[:4])  
        month    =  int(date[4:6])
        day      =  int(date[6:8])
                
        date_time = dt.datetime(year,month,day)
        
        return date_time
        
    if len(date) == 12 or len(date) == 14:

        year     =  int(date[:4])  
        month    =  int(date[4:6])
        day      =  int(date[6:8])
        hour     =  int(date[8:10])
        minute   =  int(date[10:12])
        
        date_time = dt.datetime(year,month,day, hour, minute)
        
        return date_time
    else:
        return 0



def collect_path_with_string(subject_path, patterns):
    """Returns all paths with the given patterns in the directory.
    Also check if there is a found path
    Arguments:
        data_path: directory the search starts from.
        pattern: patter of a file to be recognized.
    Returns:
        a sorted list of all paths starting from the root of the file
        system.
        
        boolean found path
    """
      
    ist_mask_there = False
    patterns = [pattern.lower() for pattern in patterns ]
    
    found_paths = []
    all_files = []
    
    for pattern in patterns:
        for roots,dirs,files in os.walk(subject_path):
            for name in files:
                if pattern not in name.lower():
                    found_paths.append(roots + '/' + name)   
                all_files.append(roots + '/' + name)   
 
    found_files = []       
           
    for all_file in all_files: 
        if all_file not in found_paths:
            found_files.append(all_file)
            ist_mask_there = True
            
    found_union_paths = list(set(found_files))
    
    found_union_paths.sort()
    
    return found_union_paths, ist_mask_there


def check_session_dir(subject_path, list_of_mask):
    """Check if the correct directory is given"""

    list_session_dir = []
    
    list_session_dir_with_mask = []
    
    found_mask_name = ""
    
    masks = []
    
    found_mask_paths = []
    
    
    for file_index, file_directory in enumerate(os.listdir(subject_path)):
 
        if is_directory(file_directory) and "csb" in file_directory.lower():   
            list_session_dir.append(file_directory)
            
    # list_session_dir.sort()
    
    for dir_name in list_session_dir:
       # res = ""
       for mask_path in list_of_mask:
           mask_name = os.path.basename(mask_path)  
           masks.append(mask_name)
           
           if get_nummeric_only(dir_name.lower()) == get_nummeric_only(mask_name.lower()):    
           
                list_session_dir_with_mask.append(dir_name)
                found_mask_name = mask_name
                
   
    list_session_dir_with_mask.sort()   
    
    if list_session_dir_with_mask:
        for mask_path in list_of_mask:
            if list_session_dir_with_mask[0] in os.path.basename(mask_path):
                found_mask_name = os.path.basename(mask_path)
                
                found_mask_paths.append(mask_path)

    if list_session_dir_with_mask and found_mask_paths:
        return list_session_dir_with_mask[0],found_mask_name, found_mask_paths
    else:
        return 0,0,0
    
def elimenate_quote(string):
    """eliminating quote  like " and ' """

    for i, c in enumerate(string):
        if i==0:
            begin = c
        end = c 
        
    if begin == '"' and end == '"':
        return string[1:-1]
    if begin == "'" and end == "'":
        return string[1:-1] 
        
    else:
        return string 
    
# check_session_dir(subject_path,list_of_mask)



# info2 = get_sessions(df_manual, "Ordner ID", int(subject_directory))




def get_sessions(df, key ,subject_id):
    
    
    """"""
    b = False
    c = False
    
    o = 0
    
    # df = df_manual
    # key="Ordner ID"
    # subject_id = 1000005
    
    for i, value in enumerate(df[key]):
        if value == subject_id:
            b  = True
            index = df.loc[df[key] == value].index.item()
           
        if isNaN(value) and b:
            c = True
            o +=1
            
        if not isNaN(value) and b and c:
            break
        
    if b:
        return df.iloc[index:index+o+1]  
    else:
        return pd.DataFrame()
     


    
temp_dir = "/home/temuuleu/PROSCIS/CSB/S-PROSCIS_MRT/persDaten/MRT_daten_BIDS/tmp_dcm2bids"    
    
    
proscis_path = "/home/temuuleu/PROSCIS/CSB/S-PROSCIS_MRT/persDaten/"
os.chdir(proscis_path)

data_path_2 = "/home/temuuleu/PROSCIS/CSB/S-PROSCIS_MRT/persDaten/MRT_daten_auto"

data_path_1 = "/home/temuuleu/PROSCIS/CSB/S-PROSCIS_MRT/persDaten/MRT_daten_manual"

bids_path  = "/home/temuuleu/PROSCIS/CSB/S-PROSCIS_MRT/persDaten/tmp2_dcm2bids"

mask_patter = ["infarct", "flair"]


path_list = [data_path_1, data_path_2]

path_list_name = ["manual", "auto"]

label_pattern = ["infarct", "flair", "csb"]

label_pattern1 = ["mt"]

#remove directory
os.system('rm -rf '+bids_path)
#create bids directory
create_dir(bids_path)

workbook = Workbook()
sheet = workbook.active

new_subject_index = 1;


#xml columns are brider
for Letter in list(string.ascii_uppercase):
    sheet.column_dimensions[Letter].width = 45
    
    
    

#writing the column    


elements_first = ['Subject-ID','ID','TYPE']


elements = ["Patient's Sex", "Patient's Birth Date", \
            "Patient's Age", "Patient's Weight",\
                "Magnetic Field Strength",
                "Spacing Between Slices"]
    
all_elements = elements_first + elements
    
    
    
first_loop = True


#df = pd.DataFrame(columns=all_elements)


df = pd.DataFrame()


df_result  = pd.DataFrame()


proscis_path = "/home/temuuleu/PROSCIS/CSB/S-PROSCIS_MRT/persDaten/query_results_delineation_20200819.xlsx"

df_query = pd.read_excel(proscis_path, header=[0,1])


xls = pd.ExcelFile(proscis_path)
df_auto = pd.read_excel(xls, 'auto downloads')
df_manual = pd.read_excel(xls, 'manual downloads')

#test_csv = pd.read_csv(bids_path+"/" +"participants.csv") 


for path_index, data_path in enumerate(path_list):
    

    for subject_index, subject_directory in enumerate(os.listdir(data_path)):
        
        found_flair_manual    = False
        found_flair_auto      = False
        found_folder_manual   = False
        found_folder_auto     = False
        #save the excell in each iteration
        #workbook.save(bids_path+"/" +"participants.xlsx")
        
        df.to_csv(bids_path+"/" +"participants.csv")  
        
        subject_path = os.path.join(data_path, subject_directory)
        subject_path = path_converter(subject_path)
        
        #check if there is a mask or dcm files
        list_of_mask, ist_mask_there = collect_path_with_string(subject_path, label_pattern)
        
        
        session_name, maske_name, found_mask_paths = check_session_dir(subject_path,list_of_mask)
               
        if len(get_feature_paths(subject_path)) > 0 and ist_mask_there and found_mask_paths:    
            # #write the subject id to excel
            # sheet["A"+str(new_subject_index+1) ] = 'sub-'+str(new_subject_index) \
            #     +" : "+ path_list_name[path_index] +subject_directory
            
            #subject directory to create
            new_subject_dir = bids_path+ "/sub-"+str(new_subject_index)
        
            #get the session dir with the earliest date
            
        
            files_path = os.path.join(subject_path, session_name)
            
            #prepare the name of the new directory
            new_file_dir = new_subject_dir+"/session-1"

            found_class_path = ''
            found_class_directory_name = ''
            #prepare the new directory for label and data directorys
            new_class_dir = new_file_dir+"/flair"
            new_data_dir = new_class_dir+"/image"
            new_mask_dir = new_class_dir+"/mask"
            
            #search for correct flair directory and check if it contains
            for class_index, class_directory in enumerate(os.listdir(files_path)):  
                if is_directory(class_directory) and "flair" in class_directory.lower()\
                    and not "cor" in class_directory.lower() and not "sag" in class_directory.lower():
                    
                    class_path = os.path.join(files_path, class_directory)
                    if len(get_feature_paths(class_path)) > 0: 
                        found_class_path = class_path
                        found_class_directory_name = class_directory
                        
                elif "darkfluid" in class_directory.lower() or "fl_" in class_directory.lower()\
                    and not "cor" in class_directory.lower() and not "sag" in class_directory.lower():
                    class_path = os.path.join(files_path, class_directory)
                    
                    if len(get_feature_paths(class_path)) > 0: 
                        found_class_path = class_path
                        found_class_directory_name = class_directory
                            
            if found_class_path:
                #if the correct directory is found iterate subject id
                new_subject_index += 1
                #create image directory
                create_dir(new_data_dir)
                #create mask directory
                create_dir(new_mask_dir)
                                
                for mask_path in found_mask_paths:
                    command = "cp "+path_converter(mask_path)+" "+ path_converter(new_mask_dir)
                    os.system(command)
                   
                for f_index, file in enumerate(os.listdir(found_class_path)):
                    
                    if "001.dcm" in file:
                        first_dcm_file = file
                    
                dataset = pydicom.dcmread(found_class_path+"/"+first_dcm_file )
                
                #myprint(dataset)
                thisdict = {
                  'Subject-ID' : 'sub-'+str(new_subject_index-1),
                  'ID'         : subject_directory,
                  'TYPE'       : path_list_name[path_index]
                }
                
                
                for data_index, data_element in enumerate(dataset): 
                    for element_index, element in enumerate(elements):    
                        if elements[element_index] in data_element.name:      
                            patient_info = repr(data_element.value) 
                            if "Patient's Birth Date" in elements[element_index]:
                                birthdate = convert_date(patient_info).strftime("%d %b %Y")
                                thisdict[elements[element_index]] = birthdate
                            elif "Patient's Age" in elements[element_index]:
                                age = elimenate_quote(get_nummeric_only(patient_info))
                                thisdict[elements[element_index]] = age
                            else:    
                                thisdict[elements[element_index]] = elimenate_quote(patient_info)
                                  
                #convert session name to datetime object
                datetime = convert_date(date_string_slipp(session_name))
                #write datetime to excel sheet
                
                thisdict['First Session Date']        = datetime.strftime("%H:%M, %A, %d, %b, %Y") 
                thisdict['Flair Directory']           = found_class_directory_name
                thisdict['Session Name']              = session_name  
                thisdict['Mask Name']                 = maske_name
                
                
                print(subject_directory)
                              
                
                #if int(new_subject_index) >= 20: break

                info = get_sessions(df_manual, "Ordner ID", int(subject_directory))
                
                
                if list(info.index):
                    info = info.loc[(info["FLAIR"] == "x" )]
                    found_flair_manual = True
                    

                if  list(info.index) and found_flair_manual:
                    info = info.loc[(info["Folder name"] == session_name )]
                    found_folder_manual = True
                    
                    
                if  list(info.index) and found_folder_manual:
                    
                    thisdict['Modality']              = info["Modality"].item() 
                    thisdict['Date']                  = info["Date"].item()  
                    thisdict['Time']                  = info["Time"].item() 
                    thisdict['Name']                  = info["Name"].item() 
                    thisdict['DOB']                   = info["DOB"].item()
                    thisdict['Patient_ID']            = info["Patient_ID"].item() 
                    thisdict['SUID']                  = info["SUID"].item()
                    thisdict['Folder name']           = info["Folder name"].item()
                    thisdict['DWI']                   = info["DWI"].item() 
                    thisdict['FLAIR']                 = info["FLAIR"].item() 
                    thisdict['LF']                    = info["LF"].item()
                    

                info = get_sessions(df_auto, "ID", int(subject_directory))
                
                
                #first_info["Folder name"] = info
                
                if list(info.index):
                
                    info = info.loc[(info["FLAIR"] == "x" )]
                    found_flair_auto = True
                    
                    
                if  list(info.index) and found_flair_auto:
                    
                    info = info.loc[(info["Folder name"] == session_name )]
                    found_folder_auto = True
                    

                if  list(info.index) and found_folder_auto:
                
                
                    thisdict['Modality']              = info["Modality"].item()   
                    thisdict['Date']                  = info["Date"].item()  
                    thisdict['Time']                  = info["Time"].item() 
                    thisdict['Name']                  = info["Name"].item() 
                    thisdict['DOB']                   = info["DOB"].item()
                    thisdict['Patient_ID']            = info["Patient_ID"].item() 
                    thisdict['SUID']                  = info["SUID"].item() 
                    thisdict['Folder name']           = info["Folder name"].item()
                    thisdict['DWI']                   = info["DWI"].item() 
                    thisdict['FLAIR']                 = info["FLAIR"].item() 
                    thisdict['LF']                    = info["LF"].item()
                    
                if  found_folder_auto == False and found_folder_manual == False:
                    
                    thisdict['Modality']              = 0
                    thisdict['Date']                  = 0
                    thisdict['Time']                  = 0
                    thisdict['Name']                  = 0
                    thisdict['DOB']                   = 0
                    thisdict['Patient_ID']            = 0
                    thisdict['SUID']                  = 0
                    thisdict['Folder name']           = 0
                    thisdict['DWI']                   = 0 
                    thisdict['FLAIR']                 = 0
                    thisdict['LF']                    = 0
                    

                df = df.append(thisdict, verify_integrity=True, ignore_index=True) 
                df = df[list(thisdict.keys())]
                

                #df_temp_result = pd.concat([df, info], axis=1, sort=False)
                
                
                """Baustelle """
                # data = df_query.loc[df_query["ID"]==int(subject_directory) ]
                
                # df_auto.loc[df_auto["ID"]==int(subject_directory)]
                # df_manual.loc[df_manual["Ordner ID"]==int(subject_directory)]
                
                # df_auto.loc[df_auto["ID"]==int('1000001')]

                # ddddd=df_manual.loc[df_manual["Ordner ID"]==int('1000002')]    
                
                #df_result = pd.concat([df_result, df_temp_result], axis=0, sort=False)
                

                df.to_excel(bids_path+"/" +"participants.xlsx") 
                
                #thisdict["First Session Date"] = str(df["First Session Date"].median())
                            
                try:
                    commad='dcm2niix -b y -z n -v n -o ' \
                    + path_converter(new_data_dir) + ' -f "%p_$s" '+path_converter(found_class_path)
                    os.system(commad)

                except OSError:
                    
                    print('Error')
                    
                #rename images    
                for new_file_index, new_file in enumerate(os.listdir(new_data_dir)):
                        
                        new_file_path = os.path.join(new_data_dir, new_file)
                        
                        os.rename(new_file_path, new_data_dir +"/subj_" \
                                  +str(new_subject_index)+"_"+session_name +"_" \
                                          +replace_typeofmri_name(new_file,"flair" ,"FLAIR"))
       

                for new_file_index, new_file in enumerate(os.listdir(new_mask_dir)):
                    
                    new_file_path = os.path.join(new_mask_dir, new_file)
                    
                    
                    os.rename(new_file_path, new_mask_dir +"/subj_" \
                              +str(new_subject_index)+"_"+session_name +"_" \
                                      +replace_typeofmri_name(new_file,"flair" ,"FLAIR"))
                    
                    
                first_loop = False;
            
                
        
        
  
        

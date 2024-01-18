# EVO Post-Multiecho-Preproc-Pipeline Lower-Level Mixed Effects Linear Model Using Feat

# Holland Brown

# Updated 2023-01-18
# Created 2023-01-18

# Between-subjects ROI analysis: Mixed-effects linear model with repeated measures

# --------------------------------------------------------------------------------------
# %%
import os
import argparse
from my_imaging_tools import fmri_tools

# Get path to subject list text file from bash options 
parser = argparse.ArgumentParser(description='Resting-state volumetric lower-level analysis')
# parser.add_argument('evo_rest_lowlev_post_MEP_vol.py') # positional argument
parser.add_argument('-s', '--subjecttextlist') # option that takes a value
args = parser.parse_args()

site = 'NKI'
timestep = '1.4' # NKI TR
# site = 'UW'
# timestep = '1.399999' # UW TR

# Important dirs
home_dir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rest/EVO_rest_volumetric'
datadir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data' # where subject folders are located
# home_dir = f'/home/holland/Desktop/EVO_TEST' # where subject folders are located
# datadir = f'{home_dir}/subjects' # where this script, atlas, and my_imaging_tools script are located

q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list
sessions = ['1','2']
runs = ['1']
# rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
rois = ['L_rACC','R_rACC']

func_fn = 'denoised_func_data_aggr' # without extension; ac/pc aligned, denoised with ICA-AROMA
feat_fn = f'evo_vol_lowerlev'
feat_df = f'{home_dir}/{feat_fn}'
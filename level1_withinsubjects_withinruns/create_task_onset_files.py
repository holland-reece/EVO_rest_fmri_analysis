# EVO Task-Based fMRI: Create Task Onset Text Files as Expected by FSL Feat

# Holland Brown

# Updated 2024-06-03
# Created 2024-06-03

# --------------------------------------------------------------------------------------
# %%
import os
import subprocess
# import argparse
from my_imaging_tools import fmri_tools

# Get path to subject list text file from bash options 
# parser = argparse.ArgumentParser(description='Resting-state volumetric lower-level analysis')
# # parser.add_argument('evo_rest_lowlev_post_MEP_vol.py') # positional argument
# parser.add_argument('-s', '--subjecttextlist') # option that takes a value
# args = parser.parse_args()

# Important dirs
# home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc
home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2'] # for Floop, there are 2 sessions (for most participants)
runs = ['1','2'] # for Floop, there are 2 runs
sites = ['NKI','UW'] # collection sites (also names of dirs)
task_name = 'floop' # task name as it appears in directories

# %%
command = [None]*2
for site in sites:
    datadir = f'{home_dir}/{site}'
    q = fmri_tools(datadir)
    for sub in q.subs:
        for session in sessions:
            for run in runs:
                onsetfile_path = f'{datadir}/{sub}/func/unprocessed/task/{task_name}/session_{session}/run_{run}'
                command[0] = f'touch {onsetfile_path}/{task_name}_S{session}_R{run}_onset.txt'

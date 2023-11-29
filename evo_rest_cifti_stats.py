# EVO Higher-Level ROI Analysis
# Create average correlation maps for each Tx condition and calculate pre- vs. post-Tx difference maps 

# Holland Brown

# Updated 2023-11-28
# Created 2023-11-28

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
# import json
import glob
from my_imaging_tools import fmri_tools

site = 'NKI'
# datadir = f'/athena/victorialab/scratch/hob4003/study_EVO' # where subject folders are located
# scriptdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rs_lower_levels' # where this script, atlas, and my_imaging_tools script are located
# wb_command = f'/software/apps/Connectome_Workbench_test/workbench/exe_rh_linux64/wb_command' # /path/to/wb_command package

datadir = f'/media/holland/EVO_Estia/EVO_MRI/organized/NKI' # where subject folders are located
scriptdir = f'/media/holland/EVO_Estia/EVO_lowerlev_avg_corrmaps' # where this script, atlas, and my_imaging_tools script are located
wb_command = f'wb_command' # /path/to/wb_command package, or just 'wb_command'

q = fmri_tools(datadir)
sessions = ['1','2']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']

# %% Calculate resting-state stats for all individual subjects
cmd = [None]*1
for sub in q.subs:
    for session in sessions:
        sub_datadir = f'{datadir}/{sub}/func/rest/session{session}'
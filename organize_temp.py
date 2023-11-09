# EVO Organize task data on cluster

# Holland Brown

# Updated 2023-11-09
# Created 2023-11-09

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
# import json
import glob
from my_imaging_tools import fmri_tools

site = 'NKI'
clusterdir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data' # where subject folders are located
scriptdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rs_lower_levels' # where this script, atlas, and my_imaging_tools script are located
drivedir = f'/Volumes/EVO_Estia/EVO_MRI/organized/{site}' # where subject folders are located

q = fmri_tools(drivedir)

# %% Rename files on hard drive
tasks = ['floop','adjective']
runs = ['1','2']
sessions = ['1','2']

cmd = [None]
for sub in q.subs:
    tdir = f'{drivedir}/{sub}/func/unprocessed/task'
    for task in tasks:
        for session in sessions:
            for run in runs:
                taskdir = f'{tdir}/{task}/session_{session}/run_{run}'
                new_filename = f'{sub}_S{session}_R{run}_{task}'
                cmd_pt1 = f"find {taskdir} -name '*.json' -exec mv "
                cmd_pt2 = "{}"
                cmd_pt3 = f" {taskdir}/{new_filename}.json"
                cmd[0] = f'{cmd_pt1}{cmd_pt2}{cmd_pt3} \;'
                q.exec_cmds(cmd)




# %%
cmd = [None]
for sub in q.subs:
    initdir = f'{drivedir}/{sub}/func/unprocessed/task'
    destdir = f'{clusterdir}/{sub}/func/unprocessed'
    cmd = f'cp -r {initdir} {destdir}'
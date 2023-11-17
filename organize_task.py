# EVO Organize task data on cluster

# Holland Brown

# Updated 2023-11-17
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

# # %% Check that task files are in the right run subdirectories before renaming
# tasks = ['floop','adjective'] # task names as they appear in your filenames and directories
# runs = ['1','2']
# sessions = ['1','2']

# cmd = [None]
# for sub in q.subs:
#     tdir = f'{drivedir}/{sub}/func/unprocessed/task'
#     for task in tasks:
#         for session in sessions:
#             for run in runs:
#                 taskdir = f'{tdir}/{task}/session_{session}/run_{run}'
#                 files = glob.glob(f'{taskdir}/*')
#                 task_and_run = f'{task}_{run}'
#                 for file in files:
#                     file_list = file.split('/')
#                     filename = file_list[-1]
#                     if task_and_run not in filename:
#                         if run == '1':
#                             cmd[0] = f'mv -vn {file} {tdir}/{task}/session_{session}/run_2'
#                             q.exec_cmds(cmd)
#                         elif run == '2':
#                             cmd[0] = f'mv -vn {file} {tdir}/{task}/session_{session}/run_1'
#                             q.exec_cmds(cmd)
                        
# # %% Rename files on hard drive
# tasks = ['floop','adjective'] # task names as they appear in your filenames and directories
# runs = ['1','2']
# sessions = ['1','2']
# extensions = ['.nii.gz','.json'] # rename both JSON and NIFTI files

# cmd = [None]
# for sub in q.subs:
#     tdir = f'{drivedir}/{sub}/func/unprocessed/task'
#     for task in tasks:
#         for session in sessions:
#             for run in runs:
#                 taskdir = f'{tdir}/{task}/session_{session}/run_{run}'
#                 new_filename = f'{sub}_S{session}_R{run}_{task}'

#                 # bash-$ find /path/to/file -name orginalFileName.extension -exec mv {} /path/to/NewFileName.extension \;
#                 # for ext in extensions:
#                 cmd_pt1 = f"find {taskdir} -name '*.json' -exec mv "
#                 cmd_pt2 = "{}"
#                 cmd_pt3 = f" {taskdir}/{new_filename}.json"
#                 cmd[0] = f'{cmd_pt1}{cmd_pt2}{cmd_pt3} \;'
#                 q.exec_cmds(cmd)

# %% Print subject sessions missing task JSON files
import os
# import json
import glob
from my_imaging_tools import fmri_tools

sites = ['NKI']
tasks = ['adjective','floop']
sessions = ['1','2']
runs = ['1','2']

missing_txt = open(f'/Users/holland_brown_ra/Desktop/evo_NKI_missing_task_jsons.txt','w')
cmd = [None]
for site in sites:
    datadir = f'/Volumes/EVO_Estia/EVO_MRI/organized/{site}'
    q = fmri_tools(datadir)
    for sub in q.subs:
        for task in tasks:
            for session in sessions:
                for run in runs:
                    taskdir = f'{datadir}/{sub}/func/unprocessed/task/{task}/session_{session}/run_{run}'
                    if os.path.isdir(taskdir):
                        # json_check = os.path.isfile(f'{taskdir}/{sub}_S{session}_R{run}_{task}.json')
                        if os.path.isfile(f'{taskdir}/{sub}_S{session}_R{run}_{task}.json') == False:
                            missing_txt.write(f'{sub}_S{session}_R{run}_{task}.json\n')

missing_txt.close()


# %% Copy renamed files from HDD to cluster dir
cmd = [None]
for sub in q.subs:
    initdir = f'{drivedir}/{sub}/func/unprocessed/task'
    destdir = f'{clusterdir}/{sub}/func/unprocessed'
    cmd[0] = f'cp -r {initdir} {destdir}'
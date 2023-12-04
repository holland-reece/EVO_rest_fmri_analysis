# EVO Organize task data on cluster

# Holland Brown

# Updated 2023-12-04
# Created 2023-11-09

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
import glob
from my_imaging_tools import fmri_tools

sites = ['NKI','UW']
# clusterdir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data' # where subject folders are located
# scriptdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rs_lower_levels' # where this script, atlas, and my_imaging_tools script are located
# drivedir = f'/Volumes/EVO_Estia/EVO_MRI/organized/{site}' # where subject folders are located

# q = fmri_tools(drivedir)
tasks = ['floop','adjective'] # task names as they appear in your filenames and directories
runs = ['1','2']
sessions = ['1','2']

# # %% Check that task files are in the right run subdirectories before renaming
# tasks = ['floop','adjective'] # task names as they appear in your filenames and directories
# runs = ['1','2']
# sessions = ['1','2']
# subs = ['97018','97019','97020','97021','97022','97023','97024','97025'] # redo; didn't copy task files correctly

# cmd = [None]
# for sub in subs:
#     tdir = f'{drivedir}/{sub}/func/unprocessed/task'
#     for task in tasks:
#         for session in sessions:
#             taskdir = f'{tdir}/{task}/session_{session}'
#             rawdir = f'/Volumes/EVO_Estia/EVO_MRI/raw/{site}/{sub}_{session}'
#             raw_taskfiles = glob.glob(f'{rawdir}/*{task}*')
#             for file in raw_taskfiles:
#                 cmd[0] = f'cp -r {file} {taskdir}'
#                 q.exec_cmds(cmd)

            # for run in runs:
            #     taskdir = f'{tdir}/{task}/session_{session}'
            #     files = glob.glob(f'{taskdir}/*')

                # task_and_run = f'{task}_{run}'
                # for file in files:
                #     file_list = file.split('/')
                #     filename = file_list[-1]
                #     if task_and_run not in filename:
                #         if run == '1':
                #             cmd[0] = f'mv -vn {file} {tdir}/{task}/session_{session}/run_2'
                #             q.exec_cmds(cmd)
                #         elif run == '2':
                #             cmd[0] = f'mv -vn {file} {tdir}/{task}/session_{session}/run_1'
                #             q.exec_cmds(cmd)
                        
# # %% Rename files on hard drive for ME Pipeline
# tasks = ['floop','adjective'] # task names as they appear in your filenames and directories
# runs = ['1','2']
# sessions = ['1','2']
# # extensions = ['.nii.gz','.json'] # rename both JSON and NIFTI files

# cmd = [None]
# for sub in q.subs:
#     tdir = f'{drivedir}/{sub}/func/unprocessed/task'
#     for task in tasks:
#         for session in sessions:
#             for run in runs:
#                 taskdir = f'{tdir}/{task}/session_{session}/run_{run}'
#                 new_filename = f'{task}_S{session}_R{run}_E{1}' # file name required for ME Pipeline

#                 # bash-$ find /path/to/file -name orginalFileName.extension -exec mv {} /path/to/NewFileName.extension \;
#                 cmd_pt1 = f"find {taskdir} -name '*.nii.gz' -exec mv "
#                 cmd_pt2 = "{}"
#                 cmd_pt3 = f" {taskdir}/{new_filename}.nii.gz"
#                 cmd[0] = f'{cmd_pt1}{cmd_pt2}{cmd_pt3} \;'
#                 q.exec_cmds(cmd)

# # %% Print subject sessions missing task JSON files
# import os
# # import json
# import glob
# from my_imaging_tools import fmri_tools

# sites = ['NKI']
# tasks = ['adjective','floop']
# sessions = ['1','2']
# runs = ['1','2']

# missing_txt = open(f'/Users/holland_brown_ra/Desktop/evo_NKI_missing_task_jsons.txt','w')
# cmd = [None]
# for site in sites:
#     datadir = f'/Volumes/EVO_Estia/EVO_MRI/organized/{site}'
#     q = fmri_tools(datadir)
#     for sub in q.subs:
#         for task in tasks:
#             for session in sessions:
#                 for run in runs:
#                     taskdir = f'{datadir}/{sub}/func/unprocessed/task/{task}/session_{session}/run_{run}'
#                     if os.path.isdir(taskdir):
#                         # json_check = os.path.isfile(f'{taskdir}/{sub}_S{session}_R{run}_{task}.json')
#                         if os.path.isfile(f'{taskdir}/{sub}_S{session}_R{run}_{task}.json') == False:
#                             missing_txt.write(f'{sub}_S{session}_R{run}_{task}.json\n')

# missing_txt.close()


# %% Copy renamed files from HDD to cluster dir
cmd = [None]*1
for site in sites:
    clusterdir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data' # where subject folders are located
    drivedir = f'/home/hob4003/thinclient_drives/EVO_Esti/EVO_MRI/organized/{site}' # where subject folders are located (copy from '/thinclient_drives')
    q = fmri_tools(drivedir)

    for sub in q.subs:
        for task in tasks:
            for session in sessions:
                for run in runs:
                    initdir = f'{drivedir}/{sub}/func/unprocessed/task/{task}/session_{session}/run_{run}'
                    destdir = f'{clusterdir}/{sub}/func/unprocessed/task/{task}/session_{session}/run_{run}'

		            # remove files currently in cluster dir that have wrong names for MEP
                    # wrongname_files = glob.glob(f'{destdir}/*')
                    # for wrongname_f in wrongname_files:    
                    cmd[0] = f'rm {destdir}/*'
                    q.exec_cmds(cmd)

		            # copy correctly-named task files from HDD to cluster dir
                    cmd[0] = f'cp -r {initdir}/* {destdir}'
                    q.exec_cmds(cmd)

                    # rm left-over files from running MEP on resting-state data
                    leftover_txt = f'{clusterdir}/{sub}/AllScans.txt'
                    if os.path.isfile(leftover_txt):
                        cmd[0] = f'rm {leftover_txt}'
                        q.exec_cmds(cmd)

# %% Get number of vols for all task files; use to check file names and dirs
# adjective should have 200 vols; floop should have 183 vols
cmd = [None]*1
sites = ['UW']
tasks = ['floop']

for site in sites:
    drivedir = f'/Volumes/EVO_Estia/EVO_MRI/organized/{site}' # where subject folders are located (copy from '/thinclient_drives')
    q = fmri_tools(drivedir)

    for sub in q.subs:
        print(f'\n')
        print(sub)

        for task in tasks:
            for session in sessions:
                for run in runs:
                    initdir = f'{drivedir}/{sub}/func/unprocessed/task/{task}/session_{session}/run_{run}'
                    cmd[0] = f'fslnvols {initdir}/{task}_S{session}_R{run}_E1.nii.gz'
                    q.exec_cmds(cmd)

# %%

import os
from my_imaging_tools import fmri_tools

sites = ['NKI','UW']

# Important dirs
# destdir = f'/home/hob4003/thinclient_drives/EVO_MRI'
# datadir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data' # where subject folders are located

# home_dir = f'/home/holland/Desktop/EVO_TEST' # where subject folders are located
# datadir = f'{home_dir}/subjects' # where this script, atlas, and my_imaging_tools script are located

# rest_func = 'denoised_func_data_aggr.nii.gz'
# task_func = ''

sessions = ['1','2']
runs = ['1']

# rois = ['L_rACC','R_rACC']
# subs = ['97018']

# cmd = [None]
# for site in sites:
#     datadir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data'
#     q = fmri_tools(f'/home/hob4003/thinclient_drives/EVO_MRI/organized/{site}') # init functions and subject list
#     for sub in q.subs:
#         for session in sessions:
#             if os.path.isdir(f'{datadir}/{sub}/func/rest/session_{session}')==True:
#                 for run in runs:
#                     restdir = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA.nii.gz'
#                     destdir = f'/home/hob4003/thinclient_drives/EVO_MRI/organized/{site}/{sub}/func'

#                     if os.path.isdir(f'{destdir}/rest')==False:
#                         cmd[0] = f'mkdir {destdir}/rest'
#                         q.exec_cmds(cmd)
#                     if os.path.isdir(f'{destdir}/rest/session_{session}')==False:
#                         cmd[0] = f'mkdir {destdir}/rest/session_{session}'
#                         q.exec_cmds(cmd)
#                     if os.path.isdir(f'{destdir}/rest/session_{session}/run_{run}')==False:
#                         cmd[0] = f'mkdir {destdir}/rest/session_{session}/run_{run}'
#                         q.exec_cmds(cmd)
#                     if os.path.isdir(f'{destdir}/rest/session_{session}/run_{run}/Rest_ICAAROMA')==False:
#                         cmd[0] = f'mkdir {destdir}/rest/session_{session}/run_{run}/Rest_ICAAROMA'
#                         q.exec_cmds(cmd)
                        
#                     cmd[0] = f'cp -r {restdir}/{rest_func} {destdir}/rest/session_{session}/run_{run}/Rest_ICAAROMA'
#                     q.exec_cmds(cmd)


rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
cmd = [None]
for site in sites:
    datadir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data'
    q = fmri_tools(f'/home/hob4003/thinclient_drives/EVO_MRI/organized/{site}')
    for sub in q.subs:
        q.exec_echo(f'\nSubject {sub}...\n')
        destdir = f'/home/hob4003/thinclient_drives/EVO_MRI/organized/{site}/{sub}'

        # copy HCP roi masks/atlas to HDD
        if os.path.isdir(f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks')==True:
            cmd[0] = f'cp -r {datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks {destdir}/anat'
            q.exec_cmds(cmd)

        # make xfms dirs in rest dir on HDD
        if os.path.isdir(f'{destdir}/func/xfms')==False:
            cmd[0] = f'mkdir {destdir}/func/xfms'
            q.exec_cmds(cmd)
        if os.path.isdir(f'{destdir}/func/xfms/rest')==False:
            cmd[0] = f'mkdir {destdir}/func/xfms/rest'
            q.exec_cmds(cmd)

        # cp T1w_acpc_brain_func file to HDD
        if os.path.isfile(f'{datadir}/{sub}/func/xfms/rest/T1w_acpc_brain_func.nii.gz')==True:
            cmd[0] = f'cp -r {datadir}/{sub}/func/xfms/rest/T1w_acpc_brain_func.nii.gz {destdir}/func/xfms/rest'
            q.exec_cmds(cmd)

        # make main rois dir
        if os.path.isdir(f'{destdir}/func/rest/rois')==False:
            cmd[0] = f'mkdir {destdir}/func/rest/rois'
            q.exec_cmds(cmd)

        for roi in rois:
            # make roi dirs
            if os.path.isdir(f'{destdir}/func/rest/rois/{roi}')==False:
                cmd[0] = f'mkdir {destdir}/func/rest/rois/{roi}'
                q.exec_cmds(cmd)

            # copy roi lower-level outputs to HDD
            if os.path.isdir(f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol')==True:
                cmd[0] = f'cp -r {datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol {destdir}/func/rest/rois/{roi}'
                q.exec_cmds(cmd)


        

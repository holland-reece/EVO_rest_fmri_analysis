# EVO Post-MEP Resting-State Higher-Level Mixed Effects Linear Model Using Python statsmodels

# Holland Brown

# Updated 2024-04-22
# Created 2024-04-22

# -----------------------------------------------------------------------------------------------

# %%
import os
import csv
import glob
import subprocess
import numpy as np
import pandas as pd
import nibabel as nib
import statsmodels.api as sm
import statsmodels.formula.api as smf
from my_imaging_tools import fmri_tools



# Set up
home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc
MNI_std_path = f'/home/holland/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz'

sessions = ['1','2']
# rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
rois = ['L_MFG'] # test
sites = ['NKI','UW'] # collection sites (also names of dirs)
# num_subjects = 55


# %% Read in Tx group labels; warp Feat outputs to standard (MNI152 1mm) space
with open('/home/holland/Desktop/EVO_Tx_groups.csv', mode ='r')as file:
    TxGroups = csv.reader(file)
    group_labels = []
    for line in TxGroups:
        group_labels.append(line)
        print(line)


cmd = [None]
for roi in rois:
    for session in sessions:
        for site in sites:
            datadir = f'{home_dir}/{site}' # where subject dirs are located
            q = fmri_tools(datadir)
            for sub in q.subs:
                if os.path.isfile(f'{feat_file_path}_MNIstd_TxGroup{Tx}.nii.gz')==False:
                    for label_pair in group_labels:
                        if label_pair[0] == sub: # label_pair is a pair containing subject ID and treatment group
                            Tx = label_pair[1] # get treatment group label for this subject
                    feat_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/cluster_mask_zstat1'
                
                    print(f'Converting {sub}, session {session}, {roi} to standard space...')
                    cmd[0] = f'fnirt --ref={MNI_std_path} --in={feat_file_path}.nii.gz --iout={feat_file_path}_MNIstd_TxGroup{Tx}.nii.gz'
                    q.exec_cmds(cmd)
    q.exec_echo('Done.')

# %% Normalize all standard-space z-score cluster maps
# cmd = [None]*2
# for roi in rois:
#     for session in sessions:
#         for site in sites:
#             datadir = f'{home_dir}/{site}' # where subject dirs are located
#             q = fmri_tools(datadir)
#             for sub in q.subs:
#                 for label_pair in group_labels:
#                     if label_pair[0] == sub: # label_pair is a pair containing subject ID and treatment group
#                         Tx = label_pair[1] # get treatment group label for this subject
#                 feat_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/cluster_mask_zstat1_MNIstd_TxGroup{Tx}'
                
                

#                 # Save bash outputs for mean and stddev
#                 q.exec_echo(f'Normalizing {sub}, session {session}, {roi}...')
#                 fslstats_cmd_str = ["fslstats", f'{feat_file_path}.nii.gz', "-M", "-S"]
#                 fslstats_output = subprocess.run(fslstats_cmd_str, capture_output=True, text=True)
#                 mean, stddev = fslstats_output.stdout.strip().split() # save mean and stddev

#                 # Normalize
#                 fslmaths_command = [
#                     "fslmaths",
#                     f'{feat_file_path}.nii.gz',
#                     "-sub", mean,
#                     "-div", stddev,
#                     f'{feat_file_path}_norm.nii.gz'
#                 ]
#                 subprocess.run(fslmaths_command)

#     q.exec_echo('Done.')



# %% Add up and average the Feat output files
cmd = [None]
Tx = '0' # run one treatment group at a time
session = '1' # run one session at a time
roi = 'L_MFG' # run one roi at a time
avg_niftis_path = f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}/{roi}_S{session}_TxGroup{Tx}_avg.nii.gz'

all_paths = glob.glob(f'{datadir}/{sites[0]}/*/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/cluster_mask_zstat1_MNIstd_TxGroup{Tx}.nii.gz',f'{datadir}/{sites[1]}/*/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/cluster_mask_zstat1_MNIstd_TxGroup{Tx}.nii.gz')
print(len(all_paths))

cmd = [None]
for nifti in all_paths:
    if nifti == all_paths[0]:
        cmd_str = f'fslmaths {nifti}'
    else:
        cmd_string = f'{cmd_str} -add {nifti}'
cmd_str = f'{cmd_str} -div {len(all_paths)} {avg_niftis_path}'



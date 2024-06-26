# EVO Higher-Level ROI Analysis
# Create average correlation maps for each Tx condition and calculate pre- vs. post-Tx difference maps 

# Holland Brown

# Updated 2023-11-22
# Created 2023-11-03

# Need condition group assignment label for each subject
    # Format labels in two text files, which code iterates through simultaneously to get subject group labels:
        # (1) subjects to be included in higher levels
        # (2) group assignments as 0 (EVO) or 1 (HC), in same order as subject list
    # I created these lists by copying columns from an Excel spreadsheet into text files

# NEXT: Troubleshoot CIFTI file format
    # can't do mixed-effects linear model with wb_command functions, and dscalar.nii incompatible with FSL, nilearn, everything
    # one option is to use volumetric data, but that would waste surface data we got from ME preproc pipeline
    # try: find a way to mask functional dtseries.nii to get ROIs, then use numpy/nilearn

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

# %% Read in labels and subjects txt files (created from excel spreadsheet)
subtxt = f'/home/holland/Desktop/EVOsubjects.txt'
labelstxt = f'/home/holland/Desktop/EVOlabels.txt'

s = open(subtxt,'r')
subs = s.readlines()
s.close()
subs = [el.strip('\n') for el in subs]
subs = [el.strip(' ') for el in subs]

l = open(labelstxt,'r')
labels = l.readlines()
l.close()
labels = [el.strip('\n') for el in labels]
labels = [el.strip(' ') for el in labels]

subs_group0 = []
subs_group1 = []

for i in range(len(subs)):
    if labels[i] == '0':
        subs_group0.append(subs[i])
    elif labels[i] == '1':
        subs_group1.append(subs[i])
group_lists = [subs_group0,subs_group1]

print(len(subs_group0))
print(len(subs_group1))

# %% Create average ROI-wholebrain correlation maps by treatment condition group
cmd=[None]
group = ''
for session in sessions:
    for roi in rois:

        # list all corr maps for this ROI and session
        corr_maps = glob.glob(f'{datadir}/*_MRI_data/*/func/rois/{roi}/*S{session}*_R1_denoised_aggr_s1.7_wholebrain_crosscorrmap.dscalar.nii')

        for group_list in group_lists:

            # get group name for output file name
            if group_list == subs_group0:
                group = 'BandTogether' # Tx group
            elif group_list == subs_group1:
                group = 'WORDS' # HC group
            print(group)
            cifti_out = f'{scriptdir}/{roi}_{group}_S{session}_avgcorrmap.dscalar.nii'

            # exclude_outliers_opt=f'-exclude-outliers <stddevs-below> <stddevs-above>'
            exclude_outliers_opt=f'' # don't exclude outliers from avg corrmap

            # list only corr maps that are in this condition group            
            group_corr_maps = []
            for sub in group_list:
                for map in corr_maps:
                    if sub in map:
                        group_corr_maps.append(map)
            print(f'Number of {group} corrmaps averaged: {len(group_corr_maps)}')

            # craft command string, then execute
            cifti_list_str = ''
            for map in group_corr_maps:
                cifti_list_str = f'{cifti_list_str} -cifti {map}'
            cmd[0] = f'{wb_command} -cifti-average {cifti_out} {exclude_outliers_opt}{cifti_list_str}'
            # q.exec_cmds(cmd)

# %% Troubleshoot CIFTI file format: Calculate pre- vs. post-Tx difference maps
import os
import subprocess
import sys
# import json
import glob
import numpy as np
from my_imaging_tools import fmri_tools

datadir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # where subject folders are located
corrmapsin_dir = f'/media/holland/EVO_Estia/EVO_ROI_analysis/EVO_ROI_higherlev/higherlev_avg_corrmaps' # where input correlation maps are located
diffmapsout_dir = f'/media/holland/EVO_Estia/EVO_ROI_analysis/EVO_ROI_higherlev/higherlev_difference_maps_v3' # where to output difference maps
wb_command = f'wb_command' # /path/to/wb_command package, or just 'wb_command'

q = fmri_tools(datadir)
sessions = ['1','2']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
conditions = ['BandTogether','WORDS'] # names of treatment condition groups, as in input corrmap file names
# num_rows = '59412' # number of rows in the corrmap cifti files (use wb_command -file-information to find this)

# Create output dir if it does not exist; don't overwrite existing dirs
# q.create_dirs(diffmapsout_dir)

# Subtract rows of time2 corrmap from rows of time1 corrmap
cmds = [None]*2
cmd = [None]
with open(f"{diffmapsout_dir}/max_vals.txt", "wb") as f:
    for roi in rois:
        for condition in conditions:
            corrmap_S1 = f'{corrmapsin_dir}/{roi}_{condition}_S1_avgcorrmap'
            corrmap_S2 = f'{corrmapsin_dir}/{roi}_{condition}_S2_avgcorrmap'
            diffmap_out = f'{diffmapsout_dir}/{roi}_{condition}_S1minusS2_diffmap'

            # DOESN'T WORK: CIFTI-MATH SUCKS
            # for cm in [corrmap_S1,corrmap_S2]:
            #     command = f'wb_command -cifti-stats {cm} -reduce MAX'
            #     get_max_val = subprocess.run(command, shell=True, executable='/bin/bash',capture_output=True)
            #     f.write(get_max_val.stdout)
            #     max = str(get_max_val.stdout.decode("utf-8"))
            #     max_v = max.replace("b'","")
            #     max_va = max_v.replace("\n'","")
            #     max_val = max_va.strip('\n')
            #     print(max_val)

            #     if cm == corrmap_S1:
            #         scaled_corrmap = f'{diffmapsout_dir}/{roi}_{condition}_S1_scaled.dscalar.nii'
            #     else:
            #         scaled_corrmap = f'{diffmapsout_dir}/{roi}_{condition}_S2_scaled.dscalar.nii'
                
            #     cmd[0] = f"{wb_command} -cifti-math 'x/abs({max_val})' -var x {cm} {scaled_corrmap}"
            #     q.exec_cmds(cmd)

            # scaled_corrmapS1 = f'{diffmapsout_dir}/{roi}_{condition}_S1_scaled.dscalar.nii'
            # scaled_corrmapS2 = f'{diffmapsout_dir}/{roi}_{condition}_S2_scaled.dscalar.nii'

            # cmd[0] = f"wb_command -cifti-math 'time2 - time1' {diffmap_out} -var time2 {scaled_corrmapS2} -select 1 1 -var time1 {scaled_corrmapS1} -select 1 1"
            # q.exec_cmds(cmd)

            # separate corrmaps into left and right hemispheres
            cmds[0] = f'{wb_command} -cifti-separate {corrmap_S1}.dscalar.nii COLUMN -metric CORTEX_LEFT {corrmap_S1}_hemisphereL.func.gii'
            cmds[1] = f'{wb_command} -cifti-separate {corrmap_S1}.dscalar.nii COLUMN -metric CORTEX_RIGHT {corrmap_S1}_hemisphereR.func.gii'
            q.exec_cmds(cmds)

            cmds[0] = f'{wb_command} -cifti-separate {corrmap_S2}.dscalar.nii COLUMN -metric CORTEX_LEFT {corrmap_S2}_hemisphereL.func.gii'
            cmds[1] = f'{wb_command} -cifti-separate {corrmap_S2}.dscalar.nii COLUMN -metric CORTEX_RIGHT {corrmap_S2}_hemisphereR.func.gii'
            q.exec_cmds(cmds)

            # convert dscalar files to txt
            # cmds[0] = f'{wb_command} -cifti-convert -to-text {corrmap_S1}.dscalar.nii {corrmap_S1}.txt'
            # cmds[1] = f'{wb_command} -cifti-convert -to-text {corrmap_S2}.dscalar.nii {corrmap_S2}.txt'
            cmds[0] = f'{wb_command} -cifti-convert -to-text {corrmap_S2}_hemisphereL.func.gii {corrmap_S2}_hemisphereL.txt'
            cmds[1] = f'{wb_command} -cifti-convert -to-text {corrmap_S2}_hemisphereR.func.gii {corrmap_S2}_hemisphereR.txt'
            q.exec_cmds(cmds)

            cmds[0] = f'{wb_command} -cifti-convert -to-text {corrmap_S1}_hemisphereL.func.gii {corrmap_S1}_hemisphereL.txt'
            cmds[1] = f'{wb_command} -cifti-convert -to-text {corrmap_S1}_hemisphereR.func.gii {corrmap_S1}_hemisphereR.txt'
            q.exec_cmds(cmds)

            # read in txt files with numpy
            corr1_L = np.loadtxt(f'{corrmap_S1}_hemisphereL.txt')
            corr2_L = np.loadtxt(f'{corrmap_S2}_hemisphereL.txt')

            corr1_R = np.loadtxt(f'{corrmap_S1}_hemisphereR.txt')
            corr2_R = np.loadtxt(f'{corrmap_S2}_hemisphereR.txt')

            # subtract the matrices row by row
            diffmat_L = corr1_L - corr2_L
            diffmat_R = corr1_R - corr2_R
            # diffmat = diffmat.round(6)
            # diffmat = diffmat.astype(np.float16)
            np.savetxt(f'{diffmap_out}_hemisphereL.txt', diffmat_L, fmt='%f')
            np.savetxt(f'{diffmap_out}_hemisphereR.txt', diffmat_R, fmt='%f')

            # convert back to CIFTI file format, using S1 corrmap as template
            cmds[0] = f'{wb_command} -cifti-convert -from-text {diffmap_out}_hemisphereL.txt {corrmap_S1}.dscalar.nii {diffmap_out}_hemisphereL.dscalar.nii'
            cmds[1] = f'{wb_command} -cifti-convert -from-text {diffmap_out}_hemisphereL.txt {corrmap_S1}.dscalar.nii {diffmap_out}_hemisphereR.dscalar.nii'
            q.exec_cmds(cmds)

            # recombine hemispheres

f.close()
# %% Troubleshoot CIFTI file format:

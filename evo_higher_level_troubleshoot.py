# EVO Higher-Level ROI Analysis
# Create average correlation maps for each Tx condition and calculate pre- vs. post-Tx difference maps 

# Holland Brown

# Updated 2023-11-20
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

# Sources:
    # Guide to Imaging Files in Nibabel: https://nbviewer.org/github/neurohackademy/nh2020-curriculum/blob/master/we-nibabel-markiewicz/NiBabel.ipynb

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
import subprocess
import sys
# import json
import glob
# from pprint import pprint
import numpy as np
import nibabel as nb
from nilearn import plotting as nlp
from my_imaging_tools import fmri_tools

datadir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # where subject folders are located
corrmapsin_dir = f'/media/holland/EVO_Estia/EVO_ROI_analysis/EVO_ROI_higherlev/higherlev_avg_corrmaps' # where input correlation maps are located
out_dir = f'/media/holland/EVO_Estia/EVO_ROI_analysis/EVO_ROI_higherlev' # where to output difference maps
wb_command = f'wb_command' # /path/to/wb_command package, or just 'wb_command'

q = fmri_tools(datadir)
sessions = ['1','2']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
conditions = ['BandTogether','WORDS'] # names of treatment condition groups, as in input corrmap file names
# num_rows = '59412' # number of rows in the corrmap cifti files (use wb_command -file-information to find this)

# Create output dir if it does not exist; don't overwrite existing dirs
# q.create_dirs(diffmapsout_dir)

# verify GPU
# if tf.test.gpu_device_name() != '/device:GPU:0':
#   print('WARNING: GPU device not found.')
# else:
#   print('SUCCESS: Found GPU: {}'.format(tf.test.gpu_device_name()))


# %% Troubleshoot CIFTI file format: convert corr mats to GIFTI hemispheres -> GIFTI files can be handled by Nibabel!!!
cmds = [None]*2
cmd = [None]

for roi in rois:
    for condition in conditions:
        corrmap_S1 = f'{corrmapsin_dir}/{roi}_{condition}_S1_avgcorrmap'
        corrmap_S2 = f'{corrmapsin_dir}/{roi}_{condition}_S2_avgcorrmap'

        baseline_left_hem = f'{corrmap_S1}_hemisphereL.func.gii'
        baseline_right_hem = f'{corrmap_S1}_hemisphereL.func.gii'
        post_left_hem = f'{corrmap_S2}_hemisphereL.func.gii'
        post_right_hem = f'{corrmap_S2}_hemisphereR.func.gii'

        # separate corrmaps into left and right hemispheres -> GIFTI files can be handled by Nibabel!!!
        cmds[0] = f'{wb_command} -cifti-separate {corrmap_S1}.dscalar.nii COLUMN -metric CORTEX_LEFT {baseline_left_hem}'
        cmds[1] = f'{wb_command} -cifti-separate {corrmap_S1}.dscalar.nii COLUMN -metric CORTEX_RIGHT {baseline_right_hem}'
        q.exec_cmds(cmds) # baseline

        cmds[0] = f'{wb_command} -cifti-separate {corrmap_S2}.dscalar.nii COLUMN -metric CORTEX_LEFT {post_left_hem}'
        cmds[1] = f'{wb_command} -cifti-separate {corrmap_S2}.dscalar.nii COLUMN -metric CORTEX_RIGHT {post_right_hem}'
        q.exec_cmds(cmds) # post

# %% Retrieve faces (triangles) and coordinates (vertices) from GIFTIs using Nibabel
for roi in rois:
    for condition in conditions:
        baseline_left_hem = f'{corrmapsin_dir}/{roi}_{condition}_S1_avgcorrmap_hemisphereL.func.gii'
        baseline_right_hem = f'{corrmapsin_dir}/{roi}_{condition}_S1_avgcorrmap_hemisphereL.func.gii'
        post_left_hem = f'{corrmapsin_dir}/{roi}_{condition}_S2_avgcorrmap_hemisphereL.func.gii'
        post_right_hem = f'{corrmapsin_dir}/{roi}_{condition}_S2_avgcorrmap_hemisphereR.func.gii'

        hemispheres = [baseline_left_hem, baseline_right_hem, post_left_hem, post_right_hem]

        for hem in hemispheres:
            func_gii = nb.load(hem) # load GIFTI containing func data projected onto surface

            # each time point is an individual data array with intent NIFTI_INTENT_TIME_SERIES; agg_data() will aggregate these into a single array
            data = func_gii.agg_data('time series')
            print(data.shape)

            # plot mean signal on an inflated surface
            # _ = nlp.plot_surf(str(data_dir / 'ds005-preproc/freesurfer/fsaverage5/surf/lh.inflated'), data.mean(axis=1))





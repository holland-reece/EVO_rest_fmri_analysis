# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-10-23
# Created 2023-09-22

# Next:
    # add read_json function to my_imaging_tools module (started)
    # troubleshoot mismatched dimensions between func data and ROI masks


# ---------------------------------------------------------------------------------------------------------------

# %%
import os
import tqdm
import json
import glob
import numpy as np
import nibabel as nib
from nilearn import signal
from scipy import stats
from my_imaging_tools import fmri_tools
# from nipype import Node, Function
# from nipype.interfaces.workbench.cifti import WBCommand

datadir = f'/home/holland/Desktop/EVO_TEST/subjects' # where subject folders are located
atlasdir = f'/home/holland/Desktop/EVO_TEST/Glasser_et_al_2016_HCP_MMP1.0_kN_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedValidation210/MNINonLinear/fsaverage_LR32k' # where HCP MMP1.0 files are located (downloaded from BALSA)
atlas_labels = f'{atlasdir}/Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors.32k_fs_LR.dlabel.nii' # HCP MMP1.0 parcel labels (either *.dlabel.nii or *.dscalar.nii files)

q = fmri_tools(datadir)
sessions = ['1','2']


# %% Create ROI mask from HCP-MMP1.0 atlas (not subject-specific)
roi = 'L_MFG' # one ROI, left or right, at a time

# names of HCP-MMP1.0 parcels for ROI
parcels = ['L_IFSa_ROI','L_46_ROI','L_p9-46v_ROI'] # L_MFG
# parcels = ['R_IFSa_ROI','R_46_ROI','R_p9-46v_ROI'] # R_MFG

command = [None]
cmd = [None]

studydir = f'/home/holland/Desktop/EVO_TEST/EVO_lower_level_ROI_masks'
roidir = f'{studydir}/{roi}'

if os.path.isdir(studydir)==False:
    q.create_dirs(studydir)
if os.path.isdir(roidir)==False:
    q.create_dirs(roidir)

# input_cifti = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
output_roi = f'{roidir}/{roi}'

# create binary ROI mask from HCP-MMP1.0 parcels
for p in parcels:
    command[0] = f'wb_command -cifti-label-to-roi {atlas_labels} {output_roi}_parc_{p}.dscalar.nii -name {p}'
    q.exec_cmds(command)

# concatenate parcels into one ROI mask, then binarize
cifti_roi_args = glob.glob(f'{roidir}/{roi}_parc*.dscalar.nii')

# cmd[0] = f"wb_command -cifti-math '(mask1 + mask2 + mask3 + mask4 + mask5 + mask6) > 0' {output_roi}_bin.dscalar.nii -var 'mask1' {cifti_roi_args[0]} -var 'mask2' {cifti_roi_args[1]} -var 'mask3' {cifti_roi_args[2]} -var 'mask4' {cifti_roi_args[3]} -var 'mask5' {cifti_roi_args[4]} -var 'mask6' {cifti_roi_args[5]}"
cmd[0] = f"wb_command -cifti-math '(mask1 + mask2 + mask3) > 0' {output_roi}_bin.dscalar.nii -var 'mask1' {cifti_roi_args[0]} -var 'mask2' {cifti_roi_args[1]} -var 'mask3' {cifti_roi_args[2]}"
q.exec_cmds(cmd)

# clean up ROI dir
parc_dir = f'{roidir}/{roi}_HCP_MMP1_parcels'
q.create_dirs(parc_dir)
for p in cifti_roi_args:
    command[0] = f'mv {p} {parc_dir}'
    q.exec_cmds(command)

# %% Extract average ROI time series from functional data using wb_command
roidir = f'{studydir}/{roi}'
roi_bin = f'{roidir}/{roi}_bin.dscalar.nii'

cmd=[None]
for sub in q.subs:
    for session in sessions:
        subject_roidir = f'{datadir}/{sub}/func/rois/{roi}'
        func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'

        cmd[0] = f'wb_command -cifti-parcellate {func_in} {atlas_labels} COLUMN {subject_roidir}/{roi}_S{session}_R1_meants.ptseries.nii -method MEAN' # dimensions should be 404 (number of timepoints) by 1
        q.exec_cmds(cmd)

# %% Use nilearn and nibabel to correlate the average ROI time series with the whole-brain resting-state data
from nilearn.input_data import NiftiLabelsMasker

roi = 'L_MFG'
studydir = f'/home/holland/Desktop/EVO_TEST/EVO_lower_level_ROI_masks'
roidir = f'{studydir}/{roi}'
roi_bin = f'{roidir}/{roi}_bin.dscalar.nii'
sessions=['1']

for sub in q.subs:
    for session in sessions:
        func_dtseries = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii' # use parcellated func (.psteries.nii) instead?
        subject_roidir = f'{datadir}/{sub}/func/rois/{roi}'
        # roi_avg = f'{subject_roidir}/{roi}_S{session}_R1_meants.ptseries.nii'

        # Load subject preprocessed functional data
        func_img = nib.load(func_dtseries)
        func_data = func_img.get_fdata()

        # Load subject average ROI time series
        # roi_img = nib.load(roi_avg)
        # roi_ts = roi_rimg.get_fdata()

        # Load generalized binary ROI mask
        roi_bin_img = nib.load(roi_bin)
        masker = NiftiLabelsMasker(labels_img=roi_bin_img, standardize=True) # z-score standardize the time series of each roi label
        #roi_ts = roi_ts.squeeze() # reduce array dimensions -> didn't change dimensions (???)

        roi_ts = masker.fit_transform(func_img)
        avg_roi_ts = np.mean(roi_ts,axis=1)
        np.savetxt(avg_roi_ts, f'{subject_roidir}/{roi}_S{session}_R1_avg_roi_ts.txt')

        # Check that time series data have same size along 0 dimension (number of rows)
        # print(func_data.shape[1] == roi_ts.shape[0])

        # Calculate correlation of ROI with func time series, voxel by voxel
        # corr_map = np.zeros(func_data.shape[0]) # init array to store corr matrix elements
        # for vox in range(func_data.shape[0]):
        #     vox_ts = func_data[vox, :] # extract time series for current voxel
        #     print(func_data.shape[1])
        #     print(vox_ts.shape[0])
        #     print(roi_ts.shape[0])

        #     # FIX: dimensions of roi_ts, vox_ts don't match!!!
        #     corr,_ = stats.pearsonr(roi_ts, vox_ts) # calculate Pearson R corr coeff for this voxel ts and avg ROI ts
        #     corr_map[vox] = corr

        # Save corr matrix as a NIFTI file
        # corr_img = nib.NiftiImage(corr_map, affine=func_img.affine)
        # nib.save(corr_img, f'{subject_roidir}/{roi}_S{session}_R1_corr_map.nii.gz')

# %% Plot the correlation matrix
from nilearn import plotting as plt

plt.plot_stat_map(corr_img, title=f"{roi}-to-Wholebrain Resting-State Correlation")
plt.show()
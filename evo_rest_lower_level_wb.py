# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-10-27
# Created 2023-09-22

# Next:
    # got -cifti-cross-correlate to produce correlation matrix; now, need -cifti-correlate version to work (dimension mismatch)
        # -cifti-cross-correlate produces map of correlation of every row of the ROI with every row of the func data
        # need -cifti-correlate version, which produces map of correlation between whole ROI and ever row of func data
    # also need to figure out how to z-score output (wb_command only offers a way to Fisher-z-score the output)

"""
Consider this procedure...
https://www.mail-archive.com/hcp-users@humanconnectome.org/msg04539.html

1) Extract mean unsmoothed ROI data to text:
wb_command -cifti-roi-average ${subject}_${run}.dtseries.nii 
roi_data_${sub}_${run}_unsmoothed.txt -vol-roi ${sub}_roi_mask.nii # probably works for surface-based ROIs as well but haven't tested
2) Convert extracted ROI data to cifti:
wb_command -cifti-create-scalar-series roi_data_${sub}_${run}_unsmoothed.txt 
roi_data_${sub}_${run}_unsmoothed.dscalar.nii -transpose -series SECOND 0 1
3) Cross-correlate this new ROI timeseries cifti with the smoothed whole-brain 
cifti data:
wb_command -cifti-cross-correlation ${subject}_${run}_smoothed.dtseries.nii roi_data_${sub}_${run}_unsmoothed.dscalar.nii correlation_${sub}_${run}.dscalar.nii
4) Repeat for all runs and average:
wb_command -cifti-average correlation_${sub}_average.dscalar.nii -cifti 
correlation_${sub}_run1.dscalar.nii -cifti correlation_${sub}_run2.dscalar.nii 
-cifti correlation_${sub}_run3.dscalar.nii -cifti 
correlation_${sub}_run4.dscalar.nii
5) Fisher z transform results:
wb_command -cifti-math "atanh(x)" z_correlation_${sub}_average.dscalar.nii -var 
x correlation_${sub}_average.dscalar.nii

"""

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
import tqdm
import json
import glob
from my_imaging_tools import fmri_tools
# from nipype import Node, Function
# from nipype.interfaces.workbench.cifti import WBCommand

datadir = f'/home/holland/Desktop/EVO_TEST/subjects' # where subject folders are located
atlasdir = f'/home/holland/Desktop/EVO_TEST/Glasser_et_al_2016_HCP_MMP1.0_kN_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedValidation210/MNINonLinear/fsaverage_LR32k' # where HCP MMP1.0 files are located (downloaded from BALSA)
atlas_labels = f'{atlasdir}/Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors.32k_fs_LR.dlabel.nii' # HCP MMP1.0 parcel labels (either *.dlabel.nii or *.dscalar.nii files)

q = fmri_tools(datadir)
sessions = ['1']


# %% Create binary ROI mask and compute roi-to-wholebrain cross-correlation maps
roi = 'R_dACC'
roidir = f'/home/holland/Desktop/EVO_TEST/EVO_lower_level_ROI_masks/{roi}'

# ROI parcel names from HCP MMP1.0 atlas labels
# roi_parcels = ['R_IFSa_ROI','R_46_ROI','R_p9-46v_ROI'] # R_MFG
# roi_parcels = ['L_IFSa_ROI','L_46_ROI','L_p9-46v_ROI'] # L_MFG
roi_parcels = ['R_p24pr_ROI','R_33pr_ROI','R_a24pr_ROI'] # R_dACC
# roi_parcels = ['L_p24pr_ROI','L_33pr_ROI','L_a24pr_ROI'] # L_dACC
# roi_parcels = ['R_p24_ROI','R_a24_ROI'] # R_rACC
# roi_parcels = ['L_p24_ROI','L_a24_ROI'] # L_rACC

# create ROI dir and parcels subdir, if needed
if os.path.isdir(roidir)==False:
    q.create_dirs(roidir)
if os.path.isdir(f'{roidir}/{roi}_HCP_MMP1_parcels')==False:
    q.create_dirs(f'{roidir}/{roi}_HCP_MMP1_parcels')

cmd = [None]*5
command=[None]
# maskcmd=[None]
for sub in q.subs:
    for session in sessions:

        # # get TR from JSON
        # with open(f'{datadir}/{sub}/func/unprocessed/session_1/run_1/Rest_S{session}_R1_E1.json', 'rt') as rest_json:
        #     rest_info = json.load(rest_json)
        # TR = rest_info['RepetitionTime']

        func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
        # func_parc = f'{datadir}/{sub}/func/rest/session_{session}/run_1/{sub}_S{session}_R1_func_s1.7_parc.ptseries.nii'

        sub_roidir = f'{datadir}/{sub}/func/rois/{roi}'
        resampled_func = f'{datadir}/{sub}/func/rest/session_{session}/run_1/{sub}_S{session}_R1_denoised_func_data_aggr_s1.7_resampled2atlas.dtseries.nii'
        # resampled_func = func_in
        roi_ts_out = f'{sub_roidir}/{sub}_{roi}_S{session}_R1_denoised_aggr_s1.7_meants'
        corrmat_out = f'{sub_roidir}/{sub}_{roi}_S{session}_R1_denoised_aggr_s1.7_wholebrain'
        # resampled_atlas = f'{datadir}/{sub}/func/resampled_Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors.32k_fs_LR.dlabel.nii'
        
        if os.path.isdir(sub_roidir)==False:
            q.create_dirs(sub_roidir)

        # resample the subject's functional data to the HCP MMP1.0 atlas space
        if os.path.isfile(resampled_func)==False:
            command[0] = f'wb_command -cifti-resample {func_in} COLUMN {atlas_labels} COLUMN ADAP_BARY_AREA ENCLOSING_VOXEL {resampled_func}'
            q.exec_cmds(command)

        # create binary ROI mask for each HCP-MMP1.0 parcel
        for p in roi_parcels:
            if os.path.isfile(f'{roidir}/{roi}_HCP_MMP1_parcels/{roi}_{p}.dscalar.nii')==False:
                command[0] = f'wb_command -cifti-label-to-roi {atlas_labels} {roidir}/{roi}_HCP_MMP1_parcels/{roi}_{p}.dscalar.nii -name {p}'
                q.exec_cmds(command)

        # concatenate parcel masks into one ROI mask, then binarize
        cifti_roi_args = glob.glob(f'{roidir}/{roi}_HCP_MMP1_parcels/{roi}_*.dscalar.nii')
        cmd[0] = f"wb_command -cifti-math '(mask1 + mask2 + mask3) > 0' {roidir}/{roi}_bin.dscalar.nii -var 'mask1' {cifti_roi_args[0]} -var 'mask2' {cifti_roi_args[1]} -var 'mask3' {cifti_roi_args[2]}"
        # cmd[0] = f"wb_command -cifti-math '(mask1 + mask2) > 0' {roidir}/{roi}_bin.dscalar.nii -var 'mask1' {cifti_roi_args[0]} -var 'mask2' {cifti_roi_args[1]}"

        # average the ROI time series from the functional dense time series
        cmd[1] = f'wb_command -cifti-roi-average {resampled_func} {roi_ts_out}.txt -cifti-roi {roidir}/{roi}_bin.dscalar.nii'

        # convert the ROI ts text file into a dense scalar file
        cmd[2] = f'wb_command -cifti-create-scalar-series {roi_ts_out}.txt {roi_ts_out}.dscalar.nii -series SECOND 0 1 -transpose'

        # cross-correlate ROI mean ts with whole-brain func data
        cmd[3] = f'wb_command -cifti-cross-correlation {resampled_func} {roi_ts_out}.dscalar.nii {corrmat_out}_crosscorrmap.dscalar.nii'
        # cmd[2] = f'wb_command -cifti-correlation {func_in} {corrmat_out}_corrmap.dscalar.nii -roi-override -cifti-roi {roi_ts_out}'

        # compute Fisher-z-scored version of correlation matrix
        cmd[4] = f'wb_command -cifti-math "atanh(x)" {corrmat_out}_crosscorrmap_fisherZ.dscalar.nii -var x {corrmat_out}_crosscorrmap.dscalar.nii'

        # resample binary mask to participant's func data
        # See: https://www.mail-archive.com/hcp-users@humanconnectome.org/msg06378.html
        # maskcmd[0] = f'wb_command -cifti-resample {roi_ts_out}.dscalar.nii COLUMN {resampled_func} COLUMN ADAP_BARY_AREA ENCLOSING_VOXEL {sub_roidir}/{roi}/{sub}_{roi}_S{session}_R1_denoised_aggr_s1.7_meants.dscalar.nii'
        # q.exec_cmds(maskcmd)

        # also compute covariance matrix
        # cmd[4] = f'wb_command -cifti-correlation {func_in} {corrmat_out}_covmap.dscalar.nii -roi-override -cifti-roi {roi_ts_out} -covariance'

        # compute correlation matrix with "no-demean" option: compute dot product of each row and normalize by diagonal
        # cmd[5] = f'wb_command -cifti-correlation {resampled_func} {corrmat_out}_corrmap_no-demean.dscalar.nii -roi-override -cifti-roi {roi_ts_out}.dscalar.nii -no-demean'

        # try -cifti-average-roi-correlation
        # cmd[5] = f'wb_command -cifti-average-roi-correlation {resampled_func} {corrmat_out}_corrmap.dscalar.nii'

        # filter by significance of p < 0.05
        # cmd[7] = f'wb_command -metric-math "(p < 0.05)" {corrmat_out}_corrmap_significant.dscalar.nii -var "p" statistical_map.func.gii'

        q.exec_cmds(cmd)


# %% Compute mask to only show activity in correlation maps that is within confidence interval
import numpy as np
import scipy.stats
from nilearn import plotting, input_data, surface
from nilearn.input_data import NiftiLabelsMasker

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a) # length of data array
    m, se = np.mean(a), scipy.stats.sem(a) # compute mean and standard error of the mean
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1) # percent point function
    return m, m-h, m+h

roi = 'L_MFG'

for sub in q.subs:
    for session in sessions:
        sub_roidir = f'{datadir}/{sub}/func/rois/{roi}'
        crosscorr_dscalar = f'{sub_roidir}/{sub}_{roi}_S{session}_R1_denoised_aggr_s1.7_wholebrain_crosscorrmap.dscalar.nii'

        # Load subject preprocessed functional data
        crosscorr = surface.load_surf_data(crosscorr_dscalar)
        corr_img = crosscorr.get_fdata()
        

# %% Plot the correlation matrix
from nilearn import plotting as plt

plt.plot_stat_map(corr_img, title=f"{roi}-to-Wholebrain Resting-State Correlation")
plt.show()

# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-10-26
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


# %% 2023-10-24 TEST: Use binary ROI mask for roi-to-wholebrain analysis
roi = 'L_MFG'
roi_parcels = ['L_IFSa_ROI','L_46_ROI','L_p9-46v_ROI'] # L_MFG parcels from HCP MMP1.0 atlas labels

my_atlas_labels = f'{atlasdir}/Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors_HRB.32k_fs_LR.dlabel.nii'
L_atlas_surf = f'{atlasdir}/Q1-Q6_RelatedValidation210.L.flat.32k_fs_LR.surf.gii'
R_atlas_surf = f'{atlasdir}/Q1-Q6_RelatedValidation210.R.flat.32k_fs_LR.surf.gii'

studydir = f'/home/holland/Desktop/EVO_TEST/EVO_lower_level_ROI_masks'
roidir = f'{studydir}/{roi}'
roi_bin = f'{roidir}/{roi}_bin.dscalar.nii'

roi_parcs_txt = f'{roidir}/{roi}_parcs.txt'
if os.path.isfile(roi_parcs_txt)==False:
    parcelstxt = open(roi_parcs_txt,'w')
    for p in roi_parcels:
        parcelstxt.write(f'{p}\n')
    parcelstxt.close()
# parcelstxt = open(roi_parcs_txt, 'r')
# roi_parcs_ls = parcelstxt.readlines()
# parcelstxt.close()

cmd = [None]*6
command=[None]
maskcmd=[None]*3
for sub in q.subs:
    for session in sessions:
        func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
        # func_parc = f'{datadir}/{sub}/func/rest/session_{session}/run_1/{sub}_S{session}_R1_func_s1.7_parc.ptseries.nii'

        sub_roidir = f'{datadir}/{sub}/func/rois/{roi}'
        # resampled_func = f'{datadir}/{sub}/func/rois/{roi}_bin_resampled2func.dscalar.nii'#denoised_func_data_aggr_s1.7_resampled2atlas.dtseries.nii'
        resampled_func = func_in
        roi_ts_out = f'{sub_roidir}/{roi}_S{session}_R1_denoised_aggr_s1.7_meants.dscalar.nii'
        corrmat_out = f'{sub_roidir}/{roi}_S{session}_R1_denoised_aggr_s1.7_wholebrain'
        resampled_atlas = f'{datadir}/{sub}/func/resampled_Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors.32k_fs_LR.dlabel.nii'
        
        if os.path.isdir(sub_roidir)==False:
            q.create_dirs(sub_roidir)

        # resample binary mask to participant's func data
        # See: https://www.mail-archive.com/hcp-users@humanconnectome.org/msg06378.html
        # maskcmd[0] = f''


        # resample the subject's functional data to the HCP MMP1.0 atlas space
        # command[0] = f'wb_command -cifti-resample {roi_bin} COLUMN {func_in} COLUMN ADAP_BARY_AREA ENCLOSING_VOXEL {resampled_func}'#_HCP_MMP1_atlas_resampled.dlabel.nii'
        command[0] = f'wb_command -cifti-resample {my_atlas_labels} COLUMN {func_in} COLUMN ADAP_BARY_AREA ENCLOSING_VOXEL {resampled_atlas}'
        q.exec_cmds(command)

        # create binary ROI mask for each HCP-MMP1.0 parcel
        for p in roi_parcels:
            if os.path.isfile(f'{sub_roidir}/{roi}_{p}_resampled2func.dscalar.nii')==False:
                command[0] = f'wb_command -cifti-label-to-roi {resampled_atlas} {sub_roidir}/{roi}_{p}_resampled2func.dscalar.nii -name {p}'
                q.exec_cmds(command)

        # concatenate parcel masks into one ROI mask, then binarize
        cifti_roi_args = glob.glob(f'{sub_roidir}/{roi}_*_resampled2func.dscalar.nii')
        cmd[0] = f"wb_command -cifti-math '(mask1 + mask2 + mask3) > 0' {sub_roidir}/{roi}_bin_resampled2func.dscalar.nii -var 'mask1' {cifti_roi_args[0]} -var 'mask2' {cifti_roi_args[1]} -var 'mask3' {cifti_roi_args[2]}"

        # average the ROI time series from the functional dense time series
        cmd[1] = f'wb_command -cifti-roi-average {func_in} {sub_roidir}/{roi}_bin.dscalar.nii -cifti-roi {sub_roidir}/{roi}_S{session}_R1_denoised_aggr_s1.7_meants.txt'

        # convert the ROI ts text file into a dense scalar file
        cmd[2] = f'wb_command -cifti-create-scalar-series {roi_ts_out} {sub_roidir}/{roi}_S{session}_R1_denoised_aggr_s1.7_meants.txt -transpose -series SECOND 0 1'

        # cross-correlate ROI mean ts with whole-brain func data
        cmd[3] = f'wb_command -cifti-cross-correlation {func_in} {roi_ts_out} {corrmat_out}_crosscorrmap.dscalar.nii'
        # cmd[2] = f'wb_command -cifti-correlation {func_in} {corrmat_out}_corrmap.dscalar.nii -roi-override -cifti-roi {roi_ts_out}'

        # compute Fisher-z-scored version of correlation matrix
        cmd[4] = f'wb_command -cifti-math "atanh(x)" {corrmat_out}_corrmap_fisherZ.dscalar.nii -var x {corrmat_out}.dscalar.nii'

        # also compute covariance matrix
        # cmd[4] = f'wb_command -cifti-correlation {func_in} {corrmat_out}_covmap.dscalar.nii -roi-override -cifti-roi {roi_ts_out} -covariance'

        # compute correlation matrix with "no-demean" option: compute dot product of each row and normalize by diagonal
        cmd[5] = f'wb_command -cifti-correlation {func_in} {corrmat_out}_corrmap_no-demean.dscalar.nii -roi-override -cifti-roi {roi_ts_out} -no-demean'

        # try -cifti-average-roi-correlation
        # cmd[6] = f'wb_command -cifti-average-roi-correlation {func_in} {corrmat_out}_corrmap_v2.dscalar.nii'

        # filter by significance of p < 0.05
        # cmd[7] = f'wb_command -metric-math "(p < 0.05)" {corrmat_out}_corrmap_significant.dscalar.nii -var "p" statistical_map.func.gii'

        q.exec_cmds(cmd)

        

# %% Use binary ROI mask for roi-to-wholebrain analysis
roi = 'L_MFG'
studydir = f'/home/holland/Desktop/EVO_TEST/EVO_lower_level_ROI_masks'
roidir = f'{studydir}/{roi}'
roi_bin = f'{roidir}/{roi}_bin.dscalar.nii'

cmd = [None]*2
for sub in q.subs:
    for session in sessions:
        func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
        sub_roidir = f'{datadir}/{sub}/func/rois/{roi}'
        if os.path.isdir(sub_roidir)==False:
            q.create_dirs(sub_roidir)

        # resample binary mask to participant's func data

        # extract average ROI time series from functional data
        cmd[0] = f'wb_command -cifti-parcellate {func_in} {atlas_labels} COLUMN {sub_roidir}/{roi}_S{session}_R1_meants.ptseries.nii -method MEAN'
        
        # take average of func time series in the ROI
        # cmd[0] = f'wb_command -cifti-roi-average ${subject}_${run}.dtseries.nii roi_data_${sub}_${run}_unsmoothed.txt -vol-roi ${sub}_roi_mask.nii'
        # cmd[0] = f'wb_command -cifti-roi-average {func_in} {sub_roidir}/{sub}_{roi}_S{session}_R1_mean.dscalar.nii -cifti-roi {roi_bin}'
        cmd[1] = f'wb_command -cifti-cross-correlation {func_in} {sub_roidir}/{roi}_S{session}_R1_meants.ptseries.nii {sub_roidir}/{roi}_S{session}_R1_rscorr.dtseries.nii'

        # convert roi text file to dscalar
        # cmd[2] = f'wb_command -cifti-create-scalar-series {roidir}/{roi}_S{session}_R1_mean.dscalar.nii {roidir}/{roi}_S{session}_R1_mean.dscalar.nii -transpose -series SECOND 0 1'

        # get correlation of average ROI time series with time series of every voxel in the brain
        # cmd[1] = f'wb_command -cifti-correlation {func_in} {roidir}/{sub}_{roi}_S{session}_R1_wholebrain_corr.dconn.nii -cifti-roi {roidir}/{sub}_{roi}_S{session}_R1_mean.dscalar.nii'

        # convert to z-scores
        # cmd[2] = f'wb_command -cifti-math "atanh(r)" {roidir}/{roi}_S{session}_R1_wholebrain_corr_zscore.dconn.nii -var "r" {roidir}/{roi}_S{session}_R1_wholebrain_corr.dconn.nii'

        # filter by significance of p < 0.05
        # cmd[4] = f'wb_command -metric-math "(p < 0.05)" {roidir}/{roi}_S{session}_R1_wholebrain_corr_zscore_significant.func.gii -var "p" statistical_map.func.gii'

        q.exec_cmds(cmd)


# %% ROI-to-wholebrain correlation
# https://www.humanconnectome.org/software/workbench-command/-cifti-average-roi-correlation

"""

wb_command -cifti-average-roi-correlation

    Averages rows for each map of the ROI(s), takes the correlation of each
    ROI average to the rest of the rows in the same file, applies the fisher
    small z transform, then averages the results across all files.  ROIs are
    always treated as weighting functions, including negative values.  For
    efficiency, ensure that everything that is not intended to be used is
    zero in the ROI map.  If -cifti-roi is specified, -left-roi, -right-roi,
    -cerebellum-roi, and -vol-roi must not be specified.  If multiple
    non-cifti ROI files are specified, they must have the same number of
    columns.

"""

# cmd = [None]*2
# for sub in tqdm(q.subs):
#     for roi_name in rois:
#         roi = f'{roidir}/{roi_name}.nii.gz' # full path to roi nifti file

#         # get TR from JSON
#         with open(f'{datadir}/{sub}/func/unprocessed/session_1/run_1/Rest_S1_E1_R1.json', 'rt') as rest_json:
#             rest_info = json.load(rest_json)
#         TR = rest_info['RepetitionTime']

#         for s in sessions:
#             subdir = f'{datadir}/{sub}/func/rest/session_{s}/run_1'
#             cifti_out = f''
#             cmd[0] = f'wb_command -cifti-average-roi-correlation {cifti_out} - output - output cifti file'

# %% Fisher z-score the data

# wb_command -cifti-math "atanh(x)" z_correlation_${sub}_average.dscalar.nii -var x correlation_${sub}_average.dscalar.nii

# %%

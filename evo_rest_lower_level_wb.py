# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-10-17
# Created 2023-09-22

# Next:
    # add read_json function to my_imaging_tools module (started)
    # figure out how to combine Glasser parcels into our ROIs

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
wb_command -cifti-cross-correlation ${subject}_${run}_smoothed.dtseries.nii 
roi_data_${sub}_${run}_unsmoothed.dscalar.nii 
correlation_${sub}_${run}.dscalar.nii
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
roi = 'MFG' # names of ROI text files containing HCP MMP1.0 ROI label names
parcels = ['L_IFSa_ROI','R_IFSa_ROI','L_46_ROI','R_46_ROI','L_p9-46v_ROI','R_p9-46v_ROI'] # names of HCP-MMP1.0 parcels for this ROI
# parcels = ['R_IFSa_ROI','R_46_ROI','R_p9-46v_ROI']
# parcels = ['IFSa', '46', 'p9-46v']
atlas_labels = f'{atlasdir}/Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors.32k_fs_LR.dlabel.nii' # HCP MMP1.0 parcel labels (either *.dlabel.nii or *.dscalar.nii files)

q = fmri_tools(datadir)
sessions = ['1','2']


# %% Create ROI mask from HCP-MMP1.0 atlas
cmd = [None]*3
for sub in q.subs:
    for session in sessions:
        subdir = f'{datadir}/{sub}/func/rois/{roi}'
        if os.path.isdir(subdir):
            input_cifti = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
            output_roi = f'{subdir}/{roi}_S{session}_R1'
            
            # create subject-specific binary ROI mask from HCP-MMP1.0 parcels
            command = [None]
            for p in parcels:
                command[0] = f'wb_command -cifti-label-to-roi {atlas_labels} {subdir}/{roi}_{p}_S{session}_R1.dscalar.nii -name {p}'
                q.exec_cmds(command)

            # concatenate parcels into our ROIs, and binarize
            parc_files = glob.glob(f'{subdir}/*dscalar.nii')
            print(len(parc_files))
            roi_parcs = []
            for pfile in parc_files:
                if (f'{roi}' in pfile) and (f'S{session}' in pfile):
                    roi_parcs.append(pfile)
            print(roi_parcs)
            cmd[0] = f"wb_command -cifti-math '(mask1 + mask2 + mask3 + mask4 + mask5 + mask6) > 0' {output_roi}_bin.dscalar.nii -var 'mask1' {roi_parcs[0]} -var 'mask2' {roi_parcs[1]} -var 'mask3' {roi_parcs[2]} -var 'mask4' {roi_parcs[3]} -var 'mask5' {roi_parcs[4]} -var 'mask6' {roi_parcs[5]}"
            # print(cmd[0])
                
            # separate roi mask into left and right GIFTI surface hemispheres
            cmd[1] = f'wb_command -cifti-separate {output_roi}_bin.dscalar.nii COLUMN -metric CORTEX_RIGHT {output_roi}_bin.R.shape.gii'
            cmd[2] = f'wb_command -cifti-separate {output_roi}_bin.dscalar.nii COLUMN -metric CORTEX_LEFT {output_roi}_bin.L.shape.gii'
            q.exec_cmds(cmd)

# %% Use binary ROI mask for roi-to-wholebrain analysis
rois = ['MFG']
hemispheres = ['L','R']
cmd = [None]*4
for sub in q.subs:
    for session in sessions:
        for hemisphere in hemispheres:
            func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
            roidir = f'{datadir}/{sub}/func/rois/{roi}'
            roi_in = f'{roidir}/{roi}_S{session}_R1_bin.{hemisphere}.shape.gii'
            
            # take average of func time series in the ROI
            # cmd[0] = f'wb_command -cifti-roi-average ${subject}_${run}.dtseries.nii roi_data_${sub}_${run}_unsmoothed.txt -vol-roi ${sub}_roi_mask.nii'
            if hemisphere == 'L':
                h = 'left'
            elif hemisphere == 'R':
                h = 'right'
            cmd[0] = f'wb_command -cifti-roi-average {func_in} {roidir}/{hemisphere}_{roi}_S{session}_R1_mean.txt -{h}-roi {roi_in}'

            # convert roi text file to dscalar
            cmd[1] = f'wb_command -cifti-create-scalar-series {roidir}/{hemisphere}_{roi}_S{session}_R1_mean.txt {roidir}/{hemisphere}_{roi}_S{session}_R1_mean.dscalar.nii -transpose -series SECOND 0 1'

            # get correlation of average ROI time series with time series of every voxel in the brain
            cmd[2] = f'wb_command -cifti-correlation {func_in} {roidir}/{hemisphere}_{roi}_S{session}_R1_wholebrain_corr.dconn.nii -cifti-roi {roidir}/{hemisphere}_{roi}_S{session}_R1_mean.dscalar.nii'

            # convert to z-scores
            cmd[3] = f'wb_command -cifti-math "atanh(r)" {roidir}/{hemisphere}_{roi}_S{session}_R1_wholebrain_corr_zscore.dconn.nii -var "r" {roidir}/{hemisphere}_{roi}_S{session}_R1_wholebrain_corr.dconn.nii'

            # filter by significance of p < 0.05
            # cmd[2] = f'wb_command -metric-math "(p < 0.05)" {roidir}/{hemisphere}_{roi}_S{session}_R1_wholebrain_corr_zscore_significant.func.gii -var "p" statistical_map.func.gii'

            q.exec_cmds(cmd)
            

# %% Cross-correlate this new ROI timeseries cifti with the smoothed whole-brain cifti data
# wb_command -cifti-cross-correlation ${subject}_${run}_smoothed.dtseries.nii 
# roi_data_${sub}_${run}_unsmoothed.dscalar.nii 
# correlation_${sub}_${run}.dscalar.nii


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

# wb_command -cifti-math "atanh(x)" z_correlation_${sub}_average.dscalar.nii -var 
# x correlation_${sub}_average.dscalar.nii

# %% Cleaning up
rois = ['MFG']
cmd = [None]
for sub in q.subs:
    parc_dir = q.create_dirs(f'{datadir}/{sub}/func/rois/{roi}/{roi}_parcels')
    for roi in rois:
        for p in parcels:
            roi_files = glob.glob(f'{datadir}/{sub}/func/rois/{roi}/*.dscalar.nii')
            for file in roi_files:
                if p in file:
                    cmd[0] = f'mv {file} {parc_dir}'
                    # q.exec_cmds(cmd)


# %%

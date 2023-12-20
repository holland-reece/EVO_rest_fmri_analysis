# EVO Post-Multiecho-Preproc-Pipeline Lower-Level Mixed Effects Linear Model Using Feat

# Holland Brown

# Updated 2023-12-20
# Created 2023-11-28

# Separate linear model for each subject, 2 repeated measures (sessions), 6 ROIs

# Notes:
    # subject's anat in functional space >> /func/xfms/rest/T1w_acpc_brain_func.nii.gz

# Sources:
    # HCP-MMP1.0 projected onto fsaverage space: https://figshare.com/articles/dataset/HCP-MMP1_0_projected_on_fsaverage/3498446
    # script to create subject-specific parcellated image in fsaverage space: https://figshare.com/articles/dataset/HCP-MMP1_0_volumetric_NIfTI_masks_in_native_structural_space/4249400?file=13320527

# --------------------------------------------------------------------------------------
# %%
import os
import json
import glob
from my_imaging_tools import fmri_tools

site = 'NKI'
# datadir = f'/athena/victorialab/scratch/hob4003/study_EVO' # where subject folders are located
# scriptdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rs_lower_levels' # where this script, atlas, and my_imaging_tools script are located
# wb_command = f'/software/apps/Connectome_Workbench_test/workbench/exe_rh_linux64/wb_command' # /path/to/wb_command package

home_dir = f'/home/holland/Desktop/EVO_TEST' # where subject folders are located
datadir = f'{home_dir}/subjects' # where this script, atlas, and my_imaging_tools script are located
# fsl_template = f"/home/holland/fsl/data/standard/MNI152_T1_2mm_brain"
# wb_command = f'wb_command' # /path/to/wb_command package, or just 'wb_command'

q = fmri_tools(datadir)
sessions = ['1','2']
runs = ['1']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
# func_fn = 'denoised_func_data_aggr' # without extension; ac/pc aligned, denoised with ICA-AROMA
func_fn = 'denoised_func_data_aggr'

# %% Create ROI masks for each subject
subs = ['97048']
sessions = ['2']
# rois=['R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
rois = ['L_MFG']

identity_mat = f'/home/holland/Documents/GitHub_repos/ME-fMRI-Pipeline-double-echo-fieldmaps/res0urces/ident.mat'

cmd = [None]*5
for roi in rois:

    # ROI parcel names from HCP MMP1.0 atlas labels
    if roi == 'R_MFG':
        roi_parcels = ['R_IFSa_ROI','R_46_ROI','R_p9-46v_ROI'] # R_MFG
    elif roi == 'L_MFG':
        roi_parcels = ['L_IFSa_ROI','L_46_ROI','L_p9-46v_ROI'] # L_MFG
    elif roi == 'R_dACC':
        roi_parcels = ['R_p24pr_ROI','R_33pr_ROI','R_a24pr_ROI'] # R_dACC
    elif roi == 'L_dACC':
        roi_parcels = ['L_p24pr_ROI','L_33pr_ROI','L_a24pr_ROI'] # L_dACC
    elif roi == 'R_rACC':
        roi_parcels = ['R_p24_ROI','R_a24_ROI'] # R_rACC
    elif roi == 'L_rACC':
        roi_parcels = ['L_p24_ROI','L_a24_ROI'] # L_rACC

    for sub in subs:
        for session in sessions:
            for run in runs:
                # directories
                roidir = f'{datadir}/{sub}/func/rest/rois/{roi}/{sub}_native_space_volumetric' # output dir for volumetric roi analysis
                sub_parc_niftis_dir = f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks/masks' # subject's HCP-MMP1 roi masks dir

                # mask file names
                ref_img = f'{datadir}/{sub}/func/xfms/rest/T1w_acpc_brain_func.nii.gz' # reference image for Flirt realignment of ROI mask
                mask_out = f'{roidir}/{roi}_S{session}_R{run}'
                mask_bin_out = f'{mask_out}_bin' # binarized

                # files for time-series extraction
                func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/{func_fn}'
                roi_ts = f'{roidir}/{roi}_S{session}_R{run}_timeseries.txt'

                # Create subject volumetric ROI dir if needed
                if os.path.isdir(roidir)==False:
                    q.create_dirs(roidir)
                # if os.path.isdir(f'{roidir}/{sub}_{roi}_HCP-MMP1_vol_parcs')==False:
                    # q.create_dirs(f'{roidir}/{sub}_{roi}_HCP-MMP1_vol_parcs')

                # Structure fslmaths command string with all roi parcels
                cmd_str = f'fslmaths'
                for p in roi_parcels:
                    if p == roi_parcels[0]:
                        cmd_str = f'{cmd_str} {sub_parc_niftis_dir}/{p}'
                    else:
                        cmd_str = f'{cmd_str} -add {sub_parc_niftis_dir}/{p}'

                cmd[0] = f'{cmd_str} {mask_out}' # combine Glasser roi parcels into roi mask
                cmd[1] = f'fslreorient2std {mask_out} {mask_out}_reorient2fsl' # fix orientation of HCP-MMP1 masks to FSL standard orientation
                cmd[2] = f'flirt -in {mask_out}_reorient2fsl -ref {ref_img} -out {mask_out}_funcspace.nii.gz -applyxfm -init {datadir}/{sub}/func/xfms/rest/AvgSBref2acpc_EpiReg_init.mat'# -init {identity_mat}' # transform masks in subj anat space to func space
                # cmd[2] = f'fslmaths {mask_out}_funcspace.nii.gz -add 10000 {mask_out}_funcspace_remean.nii.gz' # recenter ROI mask at 10000
                cmd[3] = f'fslmaths {mask_out}_funcspace.nii.gz -bin -thr 0.9 {mask_bin_out}' # binarize
                cmd[4] = f'fslmeants -i {func_in}.nii.gz -o {roi_ts} -m {mask_bin_out}' # calculate mean time series; function takes (1) path to input NIfTI, (2) path to output text file, (3) path to mask NIfTI
                q.exec_cmds(cmd)


# %% Use applywarp to transform functional data to standard space (after ICA-AROMA)
# for sub in subs:
#     featdir = f'{datadir}/{sub}/rest_preproc.feat'
#     std = f'{featdir}/reg/standard.nii.gz'
#     infile = f'{featdir}/filtered_func_denois_bptf.nii.gz'
#     outfile = f'{featdir}/filt_func_denois_bptf_mni.nii.gz'
#     warpfile = f'{featdir}/reg/example_func2standard_warp.nii.gz'
#     # prematfile = f'{featdir}/reg/example_func2highres.mat'

#     cmd=f'applywarp --ref={std} --in={infile} --out={outfile} --warp={warpfile}'
#     exec_cmds([cmd])
  
# %% Extract timeseries from ROIs for input into Level 1 analysis (ref: ROI_timeseries.sh)
# fslmeants -> output avg time series of set of voxels, or indiv time series for each of specified voxels
cmd=[None]
for sub in q.subs:
    for session in sessions:
        for run in runs:
            for roi in rois:
                roidir = 
                mask = f'{roidir}/{roi}_S{session}_R{run}' # subjects binarized ROI mask
                func_nifti = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_E1_acpc.nii.gz' # subject rest func nifti
                roi_ts = f'{datadir}/{sub}/func/rest/rois/{roi}/{roi}_S{session}_R{run}_timepoints.txt' # output text file containing ROI time series

                if os.path.exists(f'{roi_ts}') == False:
                    # print(f'Extracting ROI time series for {sub}...\n')
                    cmd[0] = f'fslmeants -i {func_nifti} -o {roi_ts} -m {mask}' # calculate mean time series; function takes (1) path to input NIfTI, (2) path to output text file, (3) path to mask NIfTI
                    q.exec_cmds(cmd) # execute bash commands in system terminal
                # else:
                #     print(f'ROI time series file already exists for subject {sub}...\n')

# %% 6. Run lower-level analysis using design template (ref: first_level5.sh)
feat_fn = f''
feat_df = f''

cmd=[None]
commands = [None]*8
for sub in q.subs:
    for session in sessions:
            for run in runs:
                # func_nifti = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_E1_acpc.nii.gz'

                # Get TR (i.e. timestep) from JSON
                json = f'{datadir}/{sub}/func/unprocessed/session_{session}/run_{run}/Rest_S{session}_R1_E1.json'
                with open(f'{datadir}/{sub}/func/unprocessed/rest/session_{session}/run_{run}/Rest_S{session}_R1_E1.json', 'rt') as func_json:
                    func_info = json.load(func_json)
                timestep = func_info['RepetitionTime']
                # print(timestep)
                
                for roi in rois:
                    session_dir = f'{datadir}/{sub}/func/rest/rois/{roi}/session_{session}'
                    outdir = f'{session_dir}/run_{run}'

                    if os.path.isdir(session_dir)==False:
                        cmd[0] = f'mkdir {session_dir}'
                        q.exec_cmds(cmd)

                    if os.path.isdir(outdir)==False:
                        cmd[0] = f'mkdir {outdir}'
                        q.exec_cmds(cmd)

                    # roi_ts = f'{datadir}/{sub}/func/rest/rois/{roi}/{roi}_S{session}_R{run}_timepoints.txt'
                    roi_tn = f'{roi}_S{session}_R{run}_timepoints.txt'

                    # Create design.fsf template for this ROI
                    if os.path.isfile(f'{datadir}/{sub}/func/rest/rois/{roi}/{roi}_S{session}_R{run}_design.fsf')==False:
                        commands[0] = f'cp {feat_df} {outdir}' # copy design file into preproc dir
                        commands[1] = f"sed -i 's/ROI/{roi}/g' {outdir}/{feat_fn}"
                        commands[2] = f"sed -i 's/TIMESTEP/{timestep}/g' {outdir}/{feat_fn}"
                        commands[3] = f"sed -i 's/INPUTNIFTI/{func_fn}/g' {outdir}/{feat_fn}" # (still have to put correct path into design file before running)
                        commands[4] = f"sed -i 's/REGIONOFINTERESTTXT/{roi_tn}/g' {outdir}/{feat_fn}" # (still have to put correct path into design file before running)
                        commands[5] = f"sed -i 's/SUBJ/{sub}/g' {outdir}/{feat_fn}"
                        commands[6] = f"sed -i 's/SESSION/{session}/g' {outdir}/{feat_fn}"
                        commands[7] = f"sed -i 's/MRIRUN/{run}/g' {outdir}/{feat_fn}"
                        q.exec_cmds(commands)

                    cmd[0] = f'feat {outdir}/{feat_fn}' # run fsf file
                    q.exec_cmds(cmd)

                    print(f'\n-------- Running Feat analysis for {sub} --------\n')
print('\n-------- Feat analyses done. --------\n\n')



# %% Run linear model for each subject

# EVO Post-Multiecho-Preproc-Pipeline Lower-Level Mixed Effects Linear Model Using Feat

# Holland Brown

# Updated 2023-12-22
# Created 2023-11-28

# Separate linear model for each subject, 2 repeated measures (sessions), 6 ROIs

# Notes:
    # Run bash-$ source $FREESURFER_HOME/SetUpFreeSurfer.sh in shell before running (needed for FreeSurfer bbregister call)

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
home_dir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rest/EVO_rest_volumetric'
datadir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data' # where subject folders are located
# identity_mat = f'/athena/victorialab/scratch/hob4003/ME_Pipeline/MEF-P-HB/MultiEchofMRI-Pipeline/res0urces/ident.mat'

# home_dir = f'/home/holland/Desktop/EVO_TEST' # where subject folders are located
# datadir = f'{home_dir}/subjects' # where this script, atlas, and my_imaging_tools script are located
# identity_mat = f'/home/holland/Documents/GitHub_repos/ME-fMRI-Pipeline-double-echo-fieldmaps/res0urces/ident.mat'

q = fmri_tools(datadir)
sessions = ['1','2']
runs = ['1']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
func_fn = 'denoised_func_data_aggr' # denoised volumetric func data

# %% First, align HCP-MMP1 in subject's FreeSurfer space to subject's anatomical -> get transform matrix
cmd=[None]*2
for sub in q.subs:
    for session in sessions:
        for run in runs:
            sub_parc_niftis_dir = f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks' # path to Glasser atlas in subject func space
            glasser_atlas_in = f'{sub_parc_niftis_dir}/HCP-MMP1' # input subject atlas filename (no ext)
            glasser_atlas_out = f'{sub_parc_niftis_dir}/HCP-MMP1_denoiseaggrfunc_S{session}_R{run}' # output subject atlas filename (no ext)
            # flirt_reference = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA.nii.gz/{func_fn}' # reference for Flirt ailgnment: functional data
            flirt_reference = f'{datadir}/{sub}/func/xfms/rest/T1w_acpc_brain_func'

            if (os.path.isfile(glasser_atlas_out)==False) and (os.path.isdir(sub_parc_niftis_dir)==True):
                cmd[0] = f'fslreorient2std {glasser_atlas_in} {glasser_atlas_in}_reoriented' # reorient FS HCP-MMP1 to FSL standard orientation
                cmd[1] = f"flirt -interp nearestneighbour -in {glasser_atlas_in}_reoriented.nii.gz -ref {flirt_reference}.nii.gz -out {glasser_atlas_out}.nii.gz -omat {glasser_atlas_out}.mat" # flirt alignment to func space -> get transform matrix
                q.exec_cmds_prtsubject(cmd,f'{sub}_S{session}_R{run}')

# %% Second, concat ROI parcels into subject-specific ROI masks and align them to subjects' functional space; then, extract ROI time series
cmd = [None]*8
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

    for sub in q.subs:
        sub_parc_niftis_dir = f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks' # path to Glasser atlas in subject func space
        for session in sessions:
            for run in runs:
                glasser_atlas_out = f'{sub_parc_niftis_dir}/HCP-MMP1_denoiseaggrfunc_S{session}_R{run}.nii.gz'
                if os.path.isfile(f'{glasser_atlas_out}'):
                    # directories
                    roidir = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol' # output dir for volumetric roi analysis
                    sub_parc_niftis_dir = f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks' # subject's HCP-MMP1 roi masks dir

                    # files for mask creation & Flirt alignment
                    flirt_reference = f'{datadir}/{sub}/func/xfms/rest/T1w_acpc_brain_func'
                    mask_out = f'{roidir}/{roi}_S{session}_R{run}' # mask comprised of Glasser ROI parcels; prefix for other ROI mask output files

                    # files for time-series extraction
                    func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA.nii.gz/{func_fn}'
                    roi_ts = f'{roidir}/{roi}_S{session}_R{run}_timeseries'

                    # Create subject volumetric ROI dir if needed
                    if os.path.isdir(roidir)==False:
                        q.create_dirs(roidir)

                    # Structure fslmaths command string with all roi parcels
                    cmd_str = f'fslmaths'
                    for p in roi_parcels:
                        if p == roi_parcels[0]:
                            cmd_str = f'{cmd_str} {sub_parc_niftis_dir}/masks/{p}'
                        else:
                            cmd_str = f'{cmd_str} -add {sub_parc_niftis_dir}/masks/{p}'

                    q.exec_echo(f'{sub}_S{session}_{run}\t{roi}')

                    cmd[0] = f'{cmd_str} {mask_out}' # combine Glasser ROI parcels into roi mask with fslmaths
                    cmd[1] = f'fslreorient2std {mask_out} {mask_out}_reoriented' # reorient HCP-MMP1 masks to FSL standard orientation
                    cmd[2] = f'flirt -2D -in {mask_out}_reoriented.nii.gz -ref {flirt_reference}.nii.gz -out {mask_out}_denoiseaggrfunc.nii.gz -omat {mask_out}_denoiseaggrfunc.mat' # 2D align ROI mask with func
                    cmd[3] = f'fslmaths {func_in}.nii.gz -add 10000 {func_in}_remean.nii.gz' # recenter ROI mask at 10000
                    cmd[4] = f'fslmaths {mask_out}_denoiseaggrfunc.nii.gz -bin {mask_out}_denoiseaggrfunc_bin.nii.gz' # binarize
                    cmd[5] = f'fslmaths {mask_out}_denoiseaggrfunc.nii.gz -bin -thr 0.8 {mask_out}_denoiseaggrfunc_bin0.8.nii.gz' # binarize with threshold 0.8
                    cmd[6] = f'fslmeants -i {func_in}_remean.nii.gz -o {roi_ts}.txt -m {mask_out}_denoiseaggrfunc_bin.nii.gz' # calculate mean time series; function takes (1) path to input NIfTI, (2) path to output text file, (3) path to mask NIfTI
                    cmd[7] = f'fslmeants -i {func_in}_remean.nii.gz -o {roi_ts}_thr0.8.txt -m {mask_out}_denoiseaggrfunc_bin0.8.nii.gz' # calculate mean time series from mask with threshold 0.8
                    q.exec_cmds(cmd)
q.exec_echo('\nDone.')

# %% 6. Run lower-level analysis using design template (ref: first_level5.sh)
feat_fn = f'20231221_evo_lowerlev_test2.fsf'
feat_df = f'/home/holland/Desktop/{feat_fn}'
timestep = 1.4
rois=['R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']


cmd=[None]
commands = [None]*8
for sub in q.subs:
    for session in sessions:
            for run in runs:
                # func_nifti = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_E1_acpc.nii.gz'

                # Get TR (i.e. timestep) from JSON
                # json = f'{datadir}/{sub}/func/unprocessed/session_{session}/run_{run}/Rest_S{session}_R1_E1.json'
                # with open(f'{datadir}/{sub}/func/unprocessed/rest/session_{session}/run_{run}/Rest_S{session}_R1_E1.json', 'rt') as func_json:
                #     func_info = json.load(func_json)
                # timestep = func_info['RepetitionTime']
                # print(timestep)
                
                for roi in rois:
                    session_dir = f'{datadir}/{sub}/func/rest/rois/{roi}/{sub}_native_space_volumetric'
                    outdir = f'{session_dir}'

                    # if os.path.isdir(session_dir)==False:
                    #     cmd[0] = f'mkdir {session_dir}'
                    #     q.exec_cmds(cmd)

                    # if os.path.isdir(outdir)==False:
                    #     cmd[0] = f'mkdir {outdir}'
                    #     q.exec_cmds(cmd)

                    # roi_ts = f'{datadir}/{sub}/func/rest/rois/{roi}/{roi}_S{session}_R{run}_timepoints.txt'
                    # roi_tn = f'{roi}_S{session}_R{run}_timepoints.txt'
                    roi_ts = f'{datadir}/{sub}/func/rest/rois/{roi}/{sub}_native_space_volumetric/{roi}_S{session}_R{run}_timeseries.txt'


                    # Create design.fsf template for this ROI
                    if os.path.isfile(f'{datadir}/{sub}/func/rest/rois/{roi}/{roi}_S{session}_R{run}_design.fsf')==False:
                        commands[0] = f'cp {feat_df} {outdir}' # copy design file into preproc dir
                        commands[1] = f"sed -i 's/REGIONOFINTEREST/{roi}/g' {outdir}/{feat_fn}"
                        commands[2] = f"sed -i 's/TIMESTEP/{timestep}/g' {outdir}/{feat_fn}"
                        commands[3] = f"sed -i 's/INPUTNIFTI/{func_fn}/g' {outdir}/{feat_fn}" # (still have to put correct path into design file before running)
                        commands[4] = f"sed -i 's/REGIONOFINTERESTTXT/{roi_ts}/g' {outdir}/{feat_fn}" # (still have to put correct path into design file before running)
                        commands[5] = f"sed -i 's/SUBJ/{sub}/g' {outdir}/{feat_fn}"
                        commands[6] = f"sed -i 's/SESSION/{session}/g' {outdir}/{feat_fn}"
                        commands[7] = f"sed -i 's/MRIRUN/{run}/g' {outdir}/{feat_fn}"
                        q.exec_cmds(commands)

                    cmd[0] = f'feat {outdir}/{feat_fn}' # run fsf file
                    q.exec_cmds(cmd)

                    print(f'\n-------- Running Feat analysis for {sub} --------\n')
print('\n-------- Feat analyses done. --------\n\n')



# %% Run linear model for each subject

# EVO Post-Multiecho-Preproc-Pipeline Lower-Level Mixed Effects Linear Model Using Feat: for subcortical ROIs

# Holland Brown

# Updated 2023-05-07
# Created 2023-01-12

# Subcortical structures are not included in the HCP-MMP1 atlas, so they are prepped for the lower level FEAT analyses separately here

# Notes:
    # Run bash-$ source $FREESURFER_HOME/SetUpFreeSurfer.sh in shell before running (needed for FreeSurfer bbregister call)

# Sources:
    # HCP-MMP1.0 projected onto fsaverage space: https://figshare.com/articles/dataset/HCP-MMP1_0_projected_on_fsaverage/3498446
    # script to create subject-specific parcellated image in fsaverage space: https://figshare.com/articles/dataset/HCP-MMP1_0_volumetric_NIfTI_masks_in_native_structural_space/4249400?file=13320527

"""
Commands for extracting R/L Amygdala from HarvardOxford atlas:

fslmaths $FSLDIR/data/atlases/HarvardOxford/HarvardOxford-sub-maxprob-thr50-2mm.nii.gz -thr 18 -uthr 18 -bin right_amygdala_mask.nii.gz
fslmaths $FSLDIR/data/atlases/HarvardOxford/HarvardOxford-sub-maxprob-thr50-2mm.nii.gz -thr 50 -uthr 50 -bin right_amygdala_mask.nii.gz

"""
# --------------------------------------------------------------------------------------
# %%
import os
import json
import glob
from my_imaging_tools import fmri_tools

# Set up paths
# home_dir = f'/media/holland/EVO_Estia' # path to data, output dir, Tx labels file, etc.
home_dir = f'/Volumes/EVO_Estia' # path to data, output dir, Tx labels file, etc.
# MNI_std_path = f'/home/holland/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz' # subjects are already in this space; just need to align
MNI_std_path = f'/Users/amd_ras/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz' # subjects are already in this space; just need to align
Txlabels_csv = f'{home_dir}/EVO_rest_higherlev_vol/EVO_Tx_groups.csv' # csv containing Tx group labels

sites = ['NKI','UW']
sessions = ['1','2']
runs = ['1']
rois = ['left_amygdala','right_amygdala']

datadir = f'{home_dir}/EVO_MRI/organized'
q = fmri_tools(datadir) # init functions and subject list
timestep = 1.4


# func_fn = 'denoised_func_data_aggr' # without extension; ac/pc aligned, denoised with ICA-AROMA
func_fn = 'denoised_func_data_aggr'

# paths to Harvord-Oxford subcortical probabalistic amygdala masks in MNI space (no extension)
L_amygdala_mask = f'{home_dir}/left_amygdala_mask.nii.gz'
R_amygdala_mask = f'{home_dir}/right_amygdala_mask.nii.gz'

# %% TEST: visualize masks
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt


std_brain = nib.load(MNI_std_path)
std_brain = std_brain.get_fdata()
std_brain = std_brain[:,:,35] # select slice to display

map = nib.load(L_amygdala_mask)
map1 = map.get_fdata()
map = map1[:,:,35] # select slice to display
map = np.ma.masked_where(map == 0, map)

fig, ax = plt.subplots(1, 1, figsize=(5, 5))

# Plot WORDS! (group 1) time difference
ax.imshow(std_brain, cmap='gray', interpolation='nearest') # plot std brain in background
# color = plt.get_cmap('Reds') # set colormap theme for roi mask
ax0 = ax.imshow(map, cmap='hsv', interpolation='nearest')
ax.axis('off')

plt.tight_layout()
plt.show()

# %% First, align HCP-MMP1 in subject's FreeSurfer space to subject's anatomical -> get right pixel dims
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
command = [None]

for roi in rois:
    q.exec_echo(f'\n------------------------- {roi} -------------------------\n')

    # ROI parcel names from HCP MMP1.0 atlas labels
    if roi == 'L_Amygdala':
        roi_parcels = [L_amygdala_mni_mask]
    elif roi == 'R_Amygdala':
        roi_parcels = [R_amygdala_mni_mask]

    for sub in q.subs:
        sub_parc_niftis_dir = f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks' # path to Glasser atlas in subject func space
        for session in sessions:
            for run in runs:
                glasser_atlas_out = f'{sub_parc_niftis_dir}/HCP-MMP1_denoiseaggrfunc_S{session}_R{run}.nii.gz'
                if os.path.isfile(f'{glasser_atlas_out}'):
                    # directories
                    roidir = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol' # output dir for volumetric roi analysis
                    sub_parc_niftis_dir = f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks' # subject's HCP-MMP1 roi masks dir

                    # files/variables for mask creation & Flirt alignment
                    flirt_reference = f'{datadir}/{sub}/func/xfms/rest/T1w_acpc_brain_func'
                    mask_out = f'{roidir}/{roi}_S{session}_R{run}' # mask comprised of Glasser ROI parcels; prefix for other ROI mask output files
                    cmd_str = f'fslmaths' # init cmd string to concatenate roi parcels

                    # files for time-series extraction
                    func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA.nii.gz/{func_fn}'
                    roi_ts = f'{roidir}/{roi}_S{session}_R{run}_timeseries'

                    # Create subject volumetric ROI dir if needed
                    if os.path.isdir(roidir)==False:
                        q.create_dirs(roidir)

                    # For Harvard-Oxford amygdala ROI masks in MNI space...
                    # if roi == 'L_Amygdala' or roi == 'R_Amygdala':
                    if roi == 'L_Amygdala':
                        mni_roi_mask = L_amygdala_mni_mask
                    else:
                        mni_roi_mask = R_amygdala_mni_mask

                    command[0] = f'flirt -2D -in {mni_roi_mask}.nii.gz -ref {flirt_reference}.nii.gz -out {mask_out}_denoiseaggrfunc.nii.gz -omat {mask_out}_denoiseaggrfunc.mat' # 2D align ROI mask with func
                    command[1] = f'fslmaths {func_in}.nii.gz -add 10000 {func_in}_remean.nii.gz' # recenter ROI mask at 10000
                    command[2] = f'fslmaths {mask_out}_denoiseaggrfunc.nii.gz -bin {mask_out}_denoiseaggrfunc_bin.nii.gz' # binarize
                    command[2] = f'fslmaths {mask_out}_denoiseaggrfunc.nii.gz -thr 0.8 -bin {mask_out}_denoiseaggrfunc_bin0.8.nii.gz' # binarize
                    command[3] = f'fslmeants -i {func_in}_remean.nii.gz -o {roi_ts}.txt -m {mask_out}_denoiseaggrfunc_bin.nii.gz' # calculate mean time series; function takes (1) path to input NIfTI, (2) path to output text file, (3) path to mask NIfTI
                    command[4] = f'fslmeants -i {func_in}_remean.nii.gz -o {roi_ts}_thr0.8.txt -m {mask_out}_denoiseaggrfunc_bin0.8.nii.gz' # calculate mean time series from mask with threshold 0.8
                    q.exec_cmds(command)
                    
                    # For Glasser 2016 HCP-MMP1 ROIs in subject anatomical space...
                    # else:
                    # Structure fslmaths command string with all roi parcels
                    # for p in roi_parcels:
                    #     if p == roi_parcels[0]:
                    #         cmd_str = f'{cmd_str} {sub_parc_niftis_dir}/masks/{p}'
                    #     else:
                    #         cmd_str = f'{cmd_str} -add {sub_parc_niftis_dir}/masks/{p}'

                    # cmd[0] = f'{cmd_str} {mask_out}' # combine Glasser ROI parcels into roi mask with fslmaths
                    # cmd[1] = f'fslreorient2std {mask_out} {mask_out}_reoriented' # reorient HCP-MMP1 masks to FSL standard orientation
                    # cmd[2] = f'flirt -2D -in {mask_out}_reoriented.nii.gz -ref {flirt_reference}.nii.gz -out {mask_out}_denoiseaggrfunc.nii.gz -omat {mask_out}_denoiseaggrfunc.mat' # 2D align ROI mask with func
                    # cmd[3] = f'fslmaths {func_in}.nii.gz -add 10000 {func_in}_remean.nii.gz' # recenter ROI mask at 10000
                    # cmd[4] = f'fslmaths {mask_out}_denoiseaggrfunc.nii.gz -bin {mask_out}_denoiseaggrfunc_bin.nii.gz' # binarize
                    # cmd[5] = f'fslmaths {mask_out}_denoiseaggrfunc.nii.gz -bin -thr 0.8 {mask_out}_denoiseaggrfunc_bin0.8.nii.gz' # binarize with threshold 0.8
                    # cmd[6] = f'fslmeants -i {func_in}_remean.nii.gz -o {roi_ts}.txt -m {mask_out}_denoiseaggrfunc_bin.nii.gz' # calculate mean time series
                    # cmd[7] = f'fslmeants -i {func_in}_remean.nii.gz -o {roi_ts}_thr0.8.txt -m {mask_out}_denoiseaggrfunc_bin0.8.nii.gz' # calculate mean time series from mask with threshold 0.8
                    # q.exec_cmds(cmd)
q.exec_echo('\nDone.\n')

# %% 6. Run lower-level analysis using design template (ref: first_level5.sh)
feat_fn = f'evo_vol_lowerlev'
feat_df = f'{home_dir}/{feat_fn}'

cmd=[None]
commands = [None]*10
for sub in q.subs:
    for session in sessions:
            for run in runs:
                func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA.nii.gz/{func_fn}'
                
                for roi in rois:
                    outdir = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol'

                    if os.path.isdir(outdir)==False:
                        cmd[0] = f'mkdir {outdir}'
                        q.exec_cmds(cmd)

                    roi_ts_str = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/{roi}_S{session}_R{run}_timeseries.txt'

                    # TEST: use ';' with sed instead of '/'
                    commands[0] = f'cp {feat_df}_template.fsf {outdir}' # copy design file into preproc dir
                    commands[1] = f'mv {outdir}/{feat_fn}_template.fsf {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf'
                    # commands[0] = f"touch '/home/holland/Desktop/test.txt'"
                    commands[2] = f"sed -i 's;TIMESTEP;{timestep};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                    commands[3] = f"sed -i 's;INPUTNIFTI;{func_in};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                    commands[4] = f"sed -i 's;REGIONOFINTERESTTXT;{roi_ts_str};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                    commands[5] = f"sed -i 's;REGIONOFINTEREST;{roi};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                    commands[6] = f"sed -i 's;SUBJ;{sub};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                    commands[7] = f"sed -i 's;MRISESSION;{session};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                    commands[8] = f"sed -i 's;MRIRUN;{run};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                    commands[9] = f"sed -i 's;DATADIRSTR;{datadir};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                    q.exec_cmds(commands)

                    cmd[0] = f'feat {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf' # run fsf file
                    q.exec_cmds(cmd)

                    # print(f'\n-------- Running Feat analysis for {sub} --------\n')
# print('\n-------- Feat analyses done. --------\n\n')


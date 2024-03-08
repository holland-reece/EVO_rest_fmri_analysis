# EVO Post-MEP Resting-State Lower-Level Mixed Effects Linear Model Using FSL Feat

# Holland Brown

# Updated 2023-03-08
# Created 2023-11-28

# Separate linear model for each subject, 2 repeated measures (sessions), 6 ROIs

# Notes:
    # Run bash-$ source $FREESURFER_HOME/SetUpFreeSurfer.sh in shell before running (needed for FreeSurfer bbregister call)
    # Have copy of FSL struct in script folder, for example MNI152_T1_2mm_brain.nii.gz

# Sources:
    # HCP-MMP1.0 projected onto fsaverage space: https://figshare.com/articles/dataset/HCP-MMP1_0_projected_on_fsaverage/3498446
    # script to create subject-specific parcellated image in fsaverage space: https://figshare.com/articles/dataset/HCP-MMP1_0_volumetric_NIfTI_masks_in_native_structural_space/4249400?file=13320527

# NEXT:
    # troubleshoot Feat not working in cluster

# --------------------------------------------------------------------------------------
# %%
import os
import subprocess
# import argparse
from my_imaging_tools import fmri_tools

# Get path to subject list text file from bash options 
# parser = argparse.ArgumentParser(description='Resting-state volumetric lower-level analysis')
# # parser.add_argument('evo_rest_lowlev_post_MEP_vol.py') # positional argument
# parser.add_argument('-s', '--subjecttextlist') # option that takes a value
# args = parser.parse_args()

# Important dirs
home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
runs = ['1']
rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
sites = ['NKI','UW'] # collection sites (also names of dirs)
# rois = ['L_rACC','R_rACC']

func_fn = 'denoised_func_data_aggr' # without extension; ac/pc aligned, denoised with ICA-AROMA
feat_fn = f'evo_rest_vol_lowerlev'
feat_df = f'{home_dir}/{feat_fn}'


# %% First, align HCP-MMP1 in subject's FreeSurfer space to subject's anatomical -> get right pixel dims
cmd=[None]*2
command = [f'\n------------------------- Aligning atlas to native functional space -------------------------\n']
subprocess.run(command, shell=True, executable='/bin/bash')
for site in sites:
    datadir = f'{home_dir}/{site}' # where subject dirs are located
    q = fmri_tools(datadir)
    for sub in q.subs:
        # if os.path.isdir(f'{datadir}/{sub}/func/unprocessed/rest/session_{session}'):
        sub_parc_niftis_dir = f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks' # path to Glasser atlas in subject func space
        glasser_atlas_in = f'{sub_parc_niftis_dir}/HCP-MMP1' # input subject atlas filename (no ext)
        glasser_atlas_out = f'{sub_parc_niftis_dir}/HCP-MMP1_denoiseaggrfunc' # output subject atlas filename (no ext)
        # flirt_reference = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA.nii.gz/{func_fn}' # reference for Flirt ailgnment: functional data
        flirt_reference = f'{datadir}/{sub}/func/xfms/rest/T1w_acpc_brain_func'

        if (os.path.isfile(glasser_atlas_out)==False) and (os.path.isdir(sub_parc_niftis_dir)==True):
            q.exec_echo(f'-------- {sub}: Reorienting subject atlas; aligning to subject functional space --------')
            cmd[0] = f'fslreorient2std {glasser_atlas_in} {glasser_atlas_in}_reoriented' # reorient FS HCP-MMP1 to FSL standard orientation
            cmd[1] = f"flirt -interp nearestneighbour -in {glasser_atlas_in}_reoriented.nii.gz -ref {flirt_reference}.nii.gz -out {glasser_atlas_out}.nii.gz -omat {glasser_atlas_out}.mat" # flirt alignment to func space -> get transform matrix
            q.exec_cmds(cmd)
        elif os.path.isfile(glasser_atlas_out)==True:
            q.exec_echo(f'Subject {sub} already has a volumetric parcellation in native functional space.')
        elif os.path.isdir(sub_parc_niftis_dir)==False:
            q.exec_echo(f'Subject {sub} does not have a volumetric parcellation directory.')

# %% Second, concat ROI parcels into subject-specific ROI masks and align them to subjects' functional space; then, extract ROI time series
cmd = [None]*8
command = [None]
sessions = ['2']

for site in sites:
    datadir = f'{home_dir}/{site}' # where subject dirs are located
    q = fmri_tools(datadir)
    for roi in rois:
        command = [f'\n------------------------- Extracting time series: {roi} -------------------------\n']
        subprocess.run(command, shell=True, executable='/bin/bash')

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
                    if os.path.isfile(f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA/{func_fn}.nii.gz')==True:
                        q.exec_echo(f'{sub}_S{session}_R{run} : {roi}')
                        glasser_atlas_out = f'{sub_parc_niftis_dir}/HCP-MMP1_denoiseaggrfunc.nii.gz'
                        # if os.path.isfile(f'{glasser_atlas_out}'): #and (os.path.isfile(f'{roi_ts}_thr0.8.txt')==False):
                            # directories
                        roidir = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol' # output dir for volumetric roi analysis
                        sub_parc_niftis_dir = f'{datadir}/{sub}/anat/{sub}_HCP-MMP1_vol_roi_masks' # subject's HCP-MMP1 roi masks dir

                        # files/variables for mask creation & Flirt alignment
                        flirt_reference = f'{datadir}/{sub}/func/xfms/rest/T1w_acpc_brain_func'
                        mask_out = f'{roidir}/{roi}_S{session}_R{run}' # mask comprised of Glasser ROI parcels; prefix for other ROI mask output files
                        cmd_str = f'fslmaths' # init cmd string to concatenate roi parcels

                        # files for time-series extraction
                        func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA/{func_fn}'
                        roi_ts = f'{roidir}/{roi}_S{session}_R{run}_timeseries'

                        # Create subject volumetric ROI dir if needed
                        if os.path.isdir(f'{datadir}/{sub}/func/rest/rois/{roi}')==False:
                            q.create_dirs(f'{datadir}/{sub}/func/rest/rois/{roi}')
                        if os.path.isdir(roidir)==False:
                            q.create_dirs(roidir)
                        
                        # Structure fslmaths command string with all roi parcels
                        for p in roi_parcels:
                            if p == roi_parcels[0]:
                                cmd_str = f'{cmd_str} {sub_parc_niftis_dir}/masks/{p}'
                            else:
                                cmd_str = f'{cmd_str} -add {sub_parc_niftis_dir}/masks/{p}'

                        if os.path.isfile(f'{roi_ts}_thr0.8.txt')==False:
                            cmd[0] = f'{cmd_str} {mask_out}' # combine Glasser ROI parcels into roi mask with fslmaths
                            cmd[1] = f'fslreorient2std {mask_out} {mask_out}_reoriented' # reorient HCP-MMP1 masks to FSL standard orientation
                            cmd[2] = f'flirt -2D -in {mask_out}_reoriented.nii.gz -ref {flirt_reference}.nii.gz -out {mask_out}_denoiseaggrfunc.nii.gz -omat {mask_out}_denoiseaggrfunc.mat' # 2D align ROI mask with func
                            cmd[3] = f'fslmaths {func_in}.nii.gz -add 10000 {func_in}_remean.nii.gz' # recenter ROI mask at 10000
                            cmd[4] = f'fslmaths {mask_out}_denoiseaggrfunc.nii.gz -bin {mask_out}_denoiseaggrfunc_bin.nii.gz' # binarize
                            cmd[5] = f'fslmaths {mask_out}_denoiseaggrfunc.nii.gz -bin -thr 0.8 {mask_out}_denoiseaggrfunc_bin0.8.nii.gz' # binarize with threshold 0.8
                            cmd[6] = f'fslmeants -i {func_in}_remean.nii.gz -o {roi_ts}.txt -m {mask_out}_denoiseaggrfunc_bin.nii.gz' # calculate mean time series
                            cmd[7] = f'fslmeants -i {func_in}_remean.nii.gz -o {roi_ts}_thr0.8.txt -m {mask_out}_denoiseaggrfunc_bin0.8.nii.gz' # calculate mean time series from mask with threshold 0.8
                            q.exec_cmds(cmd)
                        elif os.path.isfile(f'{roi_ts}_thr0.8.txt')==True:
                            q.exec_echo(f'Subject {sub} already has {roi} text file...')
    q.exec_echo('Done.')

# %% 6. Run lower-level analysis using design template (ref: first_level5.sh)
cmd=[None]
commands = [None]*11
cmds = [None]*2

command = [f'\n------------------------- Running Feat lower-levels -------------------------\n']
subprocess.run(command, shell=True, executable='/bin/bash')

for site in sites:
    datadir = f'{home_dir}/{site}' # where subject dirs are located
    q = fmri_tools(datadir)

    if site == 'NKI':
        timestep = '1.4'
    elif site == 'UW':
        timestep = '1.399999'

    for sub in q.subs:
        print(f'{sub}\n')
        for session in sessions:
            # only proceed if participant has processed func file for this session
            if os.path.isdir(f'{datadir}/{sub}/func/rest/session_{session}'):
                for run in runs:
                    func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_ICAAROMA/{func_fn}'
                    # print('test1')
                    if os.path.isfile(f'{func_in}.nii.gz')==True:
                        # print(func_in)
                        
                        for roi in rois:
                            outdir = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol'

                            if os.path.isdir(outdir)==False:
                                cmd[0] = f'mkdir {outdir}'
                                q.exec_cmds(cmd)

                            roi_ts_str = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/{roi}_S{session}_R{run}_timeseries_thr0.8.txt'
                            if os.path.isfile(roi_ts_str)==False:
                                q.exec_echo(f'\n{sub} does not have an extracted {roi} timeseries file.\n')

                            # Remove first 10 volumes before running Feat (to get around issues running Feat in cluster)
                            # if os.path.isfile(f'{func_in}_rmvols.nii.gz')==False:
                            #     cmds[0] = f'cp {func_in}.nii.gz {func_in}_rmvols.nii.gz'
                            #     cmds[1] = f'fslroi {func_in}_rmvols.nii.gz {func_in}_rmvols.nii.gz 10 0'
                            #     q.exec_cmds(cmds)

                            # Search and replace variables in Feat design file
                            commands[0] = f'cp {feat_df}_template.fsf {outdir}' # copy design file into preproc dir
                            commands[1] = f'mv {outdir}/{feat_fn}_template.fsf {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf'
                            commands[2] = f"sed -i 's;TIMESTEP;{timestep};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[3] = f"sed -i 's;INPUTNIFTI;{func_in}_rmvols.nii.gz;g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[4] = f"sed -i 's;REGIONOFINTERESTTXT;{roi_ts_str};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[5] = f"sed -i 's;REGIONOFINTEREST;{roi};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[6] = f"sed -i 's;SUBJ;{sub};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[7] = f"sed -i 's;MRISESSION;{session};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[8] = f"sed -i 's;MRIRUN;{run};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[9] = f"sed -i 's;DATADIRSTR;{datadir};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            commands[10] = f"sed -i 's;FSLDIRSTR;{home_dir};g' {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf"
                            q.exec_cmds(commands)

                            q.exec_echo(f'\n-------- Running Feat analysis for {sub} --------\n')
                            cmd[0] = f'feat {outdir}/{feat_fn}_{sub}_S{session}_R{run}.fsf' # Execute Feat design file
                            q.exec_cmds(cmd)

                    else:
                        print(f'File does not exist: {func_in}')

            else:
                print(f'Directory does not exist: {datadir}/{sub}/func/rest/session_{session}')

    q.exec_echo('Done.')

# %%

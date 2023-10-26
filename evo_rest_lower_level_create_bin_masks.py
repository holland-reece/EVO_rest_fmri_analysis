# Holland Brown

# Updated 2023-10-25
# Created 2023-10-25

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
import tqdm
import json
import glob
from my_imaging_tools import fmri_tools

# def create_sphere(number_of_vertices, sphere_out):
#     cmd=[None]*4
#     cmd[0] = f'wb_command -surface-create-sphere 6000 Sphere.6k.R.surf.gii'
#       $ wb_command -surface-flip-lr Sphere.6k.R.surf.gii Sphere.6k.L.surf.gii
#       $ wb_command -set-structure Sphere.6k.R.surf.gii CORTEX_RIGHT
#       $ wb_command -set-structure Sphere.6k.L.surf.gii CORTEX_LEFT

roi = 'L_MFG'
datadir = f'/home/holland/Desktop/EVO_TEST/subjects' # where subject folders are located
maskdir = f'/home/holland/Desktop/EVO_TEST/EVO_lower_level_ROI_masks'
roidir = f'{maskdir}/{roi}'
roi_bin = f'{roidir}/{roi}_bin.dscalar.nii'

# atlas dirs and files
atlasdir = f'/home/holland/Desktop/EVO_TEST/Glasser_et_al_2016_HCP_MMP1.0_kN_RVVG/HCP_PhaseTwo/Q1-Q6_RelatedValidation210/MNINonLinear/fsaverage_LR32k' # where HCP MMP1.0 files are located (downloaded from BALSA)
atlas_labels = f'{atlasdir}/Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors.32k_fs_LR.dlabel.nii' # HCP MMP1.0 parcel labels (either *.dlabel.nii or *.dscalar.nii files)
L_atlas_surf = f'{atlasdir}/Q1-Q6_RelatedValidation210.L.flat.32k_fs_LR.surf.gii'
R_atlas_surf = f'{atlasdir}/Q1-Q6_RelatedValidation210.R.flat.32k_fs_LR.surf.gii'
L_atlas_midthickness = f'{atlasdir}/Q1-Q6_RelatedValidation210.L.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii'
R_atlas_midthickness = f'{atlasdir}/Q1-Q6_RelatedValidation210.R.midthickness_MSMAll_2_d41_WRN_DeDrift.32k_fs_LR.surf.gii'

# parcel names from HCP-MMP1 that make up our ROI
roi_parcels = ['L_IFSa_ROI','L_46_ROI','L_p9-46v_ROI'] # L_MFG

q = fmri_tools(datadir)
sessions = ['1']


# %% Create ROI mask from HCP-MMP1.0 atlas (subject-specific)
command = [None]*3
cmd = [None]

if os.path.isdir(maskdir)==False:
    q.create_dirs(maskdir)
if os.path.isdir(roidir)==False:
    q.create_dirs(roidir)

for sub in q.subs:
    for session in sessions:
        func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
        # func_parc = f'{datadir}/{sub}/func/rest/session_{session}/run_1/{sub}_S{session}_R1_func_s1.7_parc.ptseries.nii'
        sub_roidir = f'{datadir}/{sub}/func/rois/{roi}'
        subspace_atlas = f'{datadir}/{sub}/rois/{sub}_HCP-MMP1_resampled2func'
        
        # resample HCP MMP1.0 to subject's brain-ordinate space
        if os.path.isfile(subspace_atlas)==False:
            command[0] = f'wb_command -label-resample {roi_bin} {L_atlas_surf} -vertex-area {L_atlas_midthickness} {func_in} ADAP_BARY_AREA {subspace_atlas}_L.dscalar.nii'
            command[1] = f'wb_command -label-resample {roi_bin} {R_atlas_surf} -vertex-area {R_atlas_midthickness} {func_in} ADAP_BARY_AREA {subspace_atlas}_R.dscalar.nii'
            command[2] = f'wb_command -cifti-create-label {subspace_atlas}.dscalar.nii -right-label {subspace_atlas}_R.dscalar.nii -left-label {subspace_atlas}_L.dscalar.nii'
            q.exec_cmds(command)


# # input_cifti = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
# output_roi = f'{roidir}/{roi}'

# # create binary ROI mask from HCP-MMP1.0 parcels
# for p in roi_parcels:
#     command[0] = f'wb_command -cifti-label-to-roi {atlas_labels} {output_roi}_parc_{p}.dscalar.nii -name {p}'
#     q.exec_cmds(command)

# # concatenate parcels into one ROI mask, then binarize
# cifti_roi_args = glob.glob(f'{roidir}/{roi}_parc*.dscalar.nii')

# # cmd[0] = f"wb_command -cifti-math '(mask1 + mask2 + mask3 + mask4 + mask5 + mask6) > 0' {output_roi}_bin.dscalar.nii -var 'mask1' {cifti_roi_args[0]} -var 'mask2' {cifti_roi_args[1]} -var 'mask3' {cifti_roi_args[2]} -var 'mask4' {cifti_roi_args[3]} -var 'mask5' {cifti_roi_args[4]} -var 'mask6' {cifti_roi_args[5]}"
# cmd[0] = f"wb_command -cifti-math '(mask1 + mask2 + mask3) > 0' {output_roi}_bin.dscalar.nii -var 'mask1' {cifti_roi_args[0]} -var 'mask2' {cifti_roi_args[1]} -var 'mask3' {cifti_roi_args[2]}"
# q.exec_cmds(cmd)

# # clean up ROI dir
# parc_dir = f'{roidir}/{roi}_HCP_MMP1_parcels'
# q.create_dirs(parc_dir)
# for p in cifti_roi_args:
#     command[0] = f'mv {p} {parc_dir}'
#     q.exec_cmds(command)


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

cmd = [None]*5
command=[None]
maskcmd=[None]*3
for sub in q.subs:
    for session in sessions:
        func_in = f'{datadir}/{sub}/func/rest/session_{session}/run_1/Rest_ICAAROMA.nii.gz/denoised_func_data_aggr_s1.7.dtseries.nii'
        # func_parc = f'{datadir}/{sub}/func/rest/session_{session}/run_1/{sub}_S{session}_R1_func_s1.7_parc.ptseries.nii'

        sub_roidir = f'{datadir}/{sub}/func/rois/{roi}'
        resampled_func = f'{datadir}/{sub}/func/rois/{roi}_bin_resampled2func.dscalar.nii'#denoised_func_data_aggr_s1.7_resampled2atlas.dtseries.nii'
        roi_ts_out = f'{sub_roidir}/{roi}_S{session}_R1_denoised_aggr_s1.7_resampled2atlas_meants.dscalar.nii'
        corrmat_out = f'{sub_roidir}/{roi}_S{session}_R1_denoised_aggr_s1.7_wholebrain'
        

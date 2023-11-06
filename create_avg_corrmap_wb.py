# EVO Lower-level ROI analysis: Make Avg CorrMap

# Holland Brown

# Updated 2023-11-06
# Created 2023-11-03

# NOTE: have to do mean of squares or mean of absolute values maps so negative correlations don't cancel out the positive ones
# using mean of squares or absolute values means resulting maps will not capture direction (positive vs. negative) of correlations, just the strength of those relationships

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
# import json
import glob
from my_imaging_tools import fmri_tools

site = 'NKI'
# datadir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data' # where subject folders are located
# scriptdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rs_lower_levels' # where this script, atlas, and my_imaging_tools script are located
# wb_command = f'/software/apps/Connectome_Workbench_test/workbench/exe_rh_linux64/wb_command' # /path/to/wb_command package

datadir = f'/media/holland/EVO_Estia/EVO_MRI/organized/{site}' # where subject folders are located
scriptdir = f'/media/holland/EVO_Estia/EVO_lowerlev_avg_corrmaps' # where this script, atlas, and my_imaging_tools script are located
wb_command = f'wb_command' # /path/to/wb_command package, or just 'wb_command'

q = fmri_tools(datadir)
sessions = ['1','2']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
#subs = q.read_temp_sublist_txt('/athena/victorialab/scratch/hob4003/study_EVO/NKI_subjectlist.txt')

# %% Create average ROI-wholebrain correlation maps for one site
cmd=[None]
for session in sessions:
    for roi in rois:
        cifti_list_str = ''
        cifti_out = f'{scriptdir}/EVO_lower_level_avg_corrmaps/{roi}_S{session}_lowerlev_{site}avg_corrmap.dscalar.nii'
        corr_maps = glob.glob(f'{datadir}/*/func/rois/{roi}/*_R1_denoised_aggr_s1.7_wholebrain_crosscorrmap.dscalar.nii')
        # exclude_outliers_opt=f'-exclude-outliers <stddevs-below> <stddevs-above>'
        exclude_outliers_opt=f'' # don't exclude outliers from avg corrmap
        print(corr_maps)
        for map in corr_maps:
            cifti_list_str = f'{cifti_list_str} -cifti {map}'
        cmd[0] = f'{wb_command} -cifti-average {cifti_out} {exclude_outliers_opt}{cifti_list_str}'
        q.exec_cmds(cmd)

# %% Create average ROI-wholebrain correlation maps across all sites
sites = ['NKI','UW']
corr_maps = []
cmd=[None]
for session in sessions:
    for roi in rois:
        cifti_list_str = ''
        cifti_out = f'{scriptdir}/{roi}_S{session}_lowerlev_AllSitesAvg_corrmap.dscalar.nii'
        for site in sites:
            site_corr_maps = glob.glob(f'{scriptdir}/{roi}_S{session}_lowerlev_{site}avg_corrmap.dscalar.nii')
            for s in site_corr_maps:
                corr_maps.append(s)
        # exclude_outliers_opt=f'-exclude-outliers <stddevs-below> <stddevs-above>'
        exclude_outliers_opt=f'' # don't exclude outliers from avg corrmap
        print(corr_maps) # NOTE: should be same number as number of sites
        for map in corr_maps:
            cifti_list_str = f'{cifti_list_str} -cifti {map}'
        cmd[0] = f'{wb_command} -cifti-average {cifti_out} {exclude_outliers_opt}{cifti_list_str}'
        q.exec_cmds(cmd)
# %%

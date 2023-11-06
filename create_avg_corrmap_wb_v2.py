# EVO Lower-level ROI analysis: Make Avg CorrMap

# Holland Brown

# Updated 2023-11-06
# Created 2023-11-03

# average corr maps for time1 and time2; use group labels from csv files

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

grouplabels = f'' # path to csv with group labels

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


# %% Read in labels and subjects txt files (created from excel spreadsheet)
subtxt = f'/home/holland/Desktop/EVOsubjects.txt'
labelstxt = f'/home/holland/Desktop/EVOlabels.txt'

s = open(subtxt,'r')
subs = s.readlines()
s.close()
subs = [el.strip('\n') for el in subs]
subs = [el.strip(' ') for el in subs]

l = open(labelstxt,'r')
labels = l.readlines()
l.close()
labels = [el.strip('\n') for el in labels]
labels = [el.strip(' ') for el in labels]

subs_group0 = []
subs_group1 = []

for i in range(len(subs)):
    if labels[i] == '0':
        subs_group0.append(subs[i])
    elif labels[i] == '1':
        subs_group1.append(subs[i])
group_lists = [subs_group0,subs_group1]

print(len(subs_group0))
print(len(subs_group1))

# %% Create average ROI-wholebrain correlation maps across all sites
sites = ['NKI','UW']
corr_maps = []
cmd=[None]

for session in sessions:
    for roi in rois:
        corr_maps = glob.glob(f'{datadir}/*/func/rois/{roi}/*_R1_denoised_aggr_s1.7_wholebrain_crosscorrmap.dscalar.nii')

        for group_list in group_lists:
            subs = group_list
            if subs == subs_group0:
                group = 'BandTogether' # Tx group
            elif subs == subs_group1:
                group = 'WORDS' # HC group
            print(group)

            cifti_list_str = ''

            cifti_out = f'{scriptdir}/{roi}_{group}_S{session}_higherlev_corrmap.dscalar.nii'
            for site in sites:
                site_corr_maps = glob.glob(f'{scriptdir}/{roi}_S{session}_lowerlev_{site}avg_corrmap.dscalar.nii')
                for s in site_corr_maps:
                    corr_maps.append(s)
            # exclude_outliers_opt=f'-exclude-outliers <stddevs-below> <stddevs-above>'
            exclude_outliers_opt=f'' # don't exclude outliers from avg corrmap
            # print(corr_maps) # NOTE: should be same number as number of sites
            for map in corr_maps:
                cifti_list_str = f'{cifti_list_str} -cifti {map}'
            cmd[0] = f'{wb_command} -cifti-average {cifti_out} {exclude_outliers_opt}{cifti_list_str}'
            q.exec_cmds(cmd)


            cifti_out = f'{scriptdir}/EVO_lower_level_avg_corrmaps/{roi}_S{session}_lowerlev_{site}avg_corrmap.dscalar.nii'
            
            # exclude_outliers_opt=f'-exclude-outliers <stddevs-below> <stddevs-above>'
            exclude_outliers_opt=f'' # don't exclude outliers from avg corrmap
            
            group_corr_maps = []
            for sub in subs:
                for map in corr_maps:
                    if sub in map:
                        group_corr_maps.append(map)
            print(len(group_corr_maps))

            for map in group_corr_maps:
                cifti_list_str = f'{cifti_list_str} -cifti {map}'
                cmd[0] = f'{wb_command} -cifti-average {cifti_out} {exclude_outliers_opt}{cifti_list_str}'
                q.exec_cmds(cmd)
# %%

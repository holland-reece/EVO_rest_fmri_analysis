# EVO Post-MEP Resting-State Higher-Level Mixed Effects Linear Model Using Python statsmodels

# Holland Brown

# Updated 2024-04-30
# Created 2024-04-22

# NOTE: BandTogether = 0; WORDS! = 1

# -----------------------------------------------------------------------------------------------

# %%
import os
import csv
import glob
import subprocess
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from multiprocessing import Pool
import statsmodels.api as sm
import statsmodels.formula.api as smf
from my_imaging_tools import fmri_tools

def process_subject(args): # function to help parallelize fnirt command
    roi, session, site, sub, Tx = args
    home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized'
    MNI_std_path = f'/Users/holland_brown_ra/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
    # MNI_std_path = f'/Users/holland_brown_ra/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
    datadir = f'{home_dir}/{site}'
    feat_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/cope1'
    out_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/COPE_MNIstd_TxGroup{Tx}'
    
    if not os.path.isfile(out_file_path):
        print(f'Converting {sub}, session {session}, {roi} to standard space...\n')
        cmd = f'fnirt --ref={MNI_std_path} --in={feat_file_path} --iout={out_file_path}'
        subprocess.run(cmd, shell=True)

def main(): # define class to set up parallelized commands
    with open(Txlabels_csv, mode='r') as file:
        reader = csv.reader(file)
        group_labels = list(reader)

    home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc
    rois = ['L_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
    # rois = ['R_MFG']
    sessions = ['1','2']
    sites = ['NKI', 'UW']  # Define your sites

    tasks = []
    for roi in rois:
        for session in sessions:
            for site in sites:
                q = fmri_tools(f'{home_dir}/{site}')
                for sub in q.subs:
                    # extract treatment group for subject
                    Tx = next((label[1] for label in group_labels if label[0] == sub), None)
                    if Tx:
                        tasks.append((roi, session, site, sub, Tx))

    with Pool(processes=4) as pool:
        pool.map(process_subject, tasks)
        pool.close()
        pool.join()

def z_score(data):
    """Return the z-score of the array."""
    mean = np.mean(data)
    std = np.std(data)
    z_scores = (data - mean) / std
    return z_scores






# Set up paths
# home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to subject directories where lower-level Feat results are
# MNI_std_path = f'/home/holland/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
# Txlabels_csv = '/media/holland/EVO_Estia/EVO_rest_higherlev_vol/EVO_Tx_groups.csv'

home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized'
MNI_std_path = f'/Users/holland_brown_ra/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
Txlabels_csv = '/Volumes/EVO_Estia/EVO_rest_higherlev_vol/EVO_Tx_groups.csv'

sessions = ['1','2']
rois = ['L_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
# rois = ['R_MFG'] # test
sites = ['NKI','UW'] # collection sites (also names of dirs)

# num_subjects = 55

# %% Batch create and execute fnirt commands; register individual COPEs to MNI152 standard

if __name__ == '__main__':
    main()

# %% Read in Tx group labels; warp Feat outputs to standard (MNI152 1mm) space
# rois = ['R_MFG']
# sessions = ['1']


# with open(Txlabels_csv, mode ='r')as file:
#     TxGroups = csv.reader(file)
#     group_labels = []
#     for line in TxGroups:
#         group_labels.append(line)
#         print(line)


# cmd = [None]
# for roi in rois:
#     for session in sessions:
#         for site in sites:
#             datadir = f'{home_dir}/{site}' # where subject dirs are located
#             q = fmri_tools(datadir)
#             for sub in q.subs:
#                 feat_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/cope1.nii.gz'
#                 for label_pair in group_labels:
#                     if label_pair[0] == sub: # label_pair is a pair containing subject ID and treatment group
#                         Tx = label_pair[1] # get treatment group label for this subject

#                 if os.path.isfile(f'{feat_file_path}_MNIstd_COPE_TxGroup{Tx}.nii.gz')==False:
#                     print(f'Converting {sub}, session {session}, {roi} to standard space...')
#                     cmd[0] = f'fnirt --ref={MNI_std_path} --in={feat_file_path}.nii.gz --iout={feat_file_path}_MNIstd_COPE_TxGroup{Tx}.nii.gz'
#                     q.exec_cmds(cmd)

#     q.exec_echo('Done.')

# %% Normalize individual standard-space COPEs
# cmd = [None]*2
# for roi in rois:
#     for session in sessions:
#         for site in sites:
#             datadir = f'{home_dir}/{site}' # where subject dirs are located
#             q = fmri_tools(datadir)
#             for sub in q.subs:
#                 for label_pair in group_labels:
#                     if label_pair[0] == sub: # label_pair is a pair containing subject ID and treatment group
#                         Tx = label_pair[1] # get treatment group label for this subject
#                 # feat_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/cope1'
#                 feat_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/COPE_MNIstd_TxGroup{Tx}'
#                 # feat_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/cluster_mask_zstat1_MNIstd_TxGroup{Tx}'
                
                

#                 # Save bash outputs for mean and stddev
#                 # q.exec_echo(f'Warping {sub}, session {session}, {roi} to std space...')
#                 # fslstats_cmd_str = [f'fnirt --ref={MNI_std_path}', f'--in={feat_file_path}.nii.gz --iout={out_file_path}']
#                 fslstats_output = subprocess.run(fslstats_cmd_str, capture_output=True, text=True)
#                 mean, stddev = fslstats_output.stdout.strip().split() # save mean and stddev

#                 # Average all subjects together for one Tx group
#                 fslmaths_command = [
#                     "fslmaths",
#                     f'{feat_file_path}.nii.gz',
#                     "-sub", mean,
#                     "-div", stddev,
#                     f'{feat_file_path}_norm.nii.gz'
#                 ]
#                 subprocess.run(fslmaths_command)
#                 # process_subject(roi,session,site,sub,Tx)

#     q.exec_echo('Done.')



# %% Add up and average the Feat output files
cmd = [None]
Tx = '1' # run one treatment group at a time
session = '2' # run one session at a time
roi = 'L_rACC' # run one roi at a time
q = fmri_tools(home_dir)

# avg_niftis_path = f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}/{roi}_S{session}_TxGroup{Tx}_avg_cope'
# avg_niftis_path = f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}/{roi}_S{session}_COPE_MNIstd_TxGroup{Tx}_avg'
avg_niftis_path = f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}_S{session}_COPE_MNIstd_TxGroup{Tx}_avg'

all_paths = glob.glob(f'{home_dir}/{sites[0]}/*/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/COPE_MNIstd_TxGroup{Tx}.nii.gz')#,f'{home_dir}/{sites[1]}/*/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/cluster_mask_zstat1_MNIstd_TxGroup{Tx}.nii.gz')
all_paths += glob.glob(f'{home_dir}/{sites[1]}/*/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/COPE_MNIstd_TxGroup{Tx}.nii.gz')
print(len(all_paths))

cmd = [None]
for n in all_paths:
    # nlist = n.split('/')
    # nifti = n - n[-1]
    # nifti = f'{nifti}/S{session}_R1_lowerlev_vol.feat/COPE_MNIstd_TxGroup{Tx}'
    if n == all_paths[0]:
        cmd_str = f'fslmaths {n}'
    else:
        cmd_str = f'{cmd_str} -add {n}'
cmd[0] = f'{cmd_str} -div {len(all_paths)} {avg_niftis_path}'
# print(cmd) # test - copy and run in terminal
q.exec_cmds(cmd)

# # Threshold and save
# avg_niftis_path = f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}/{roi}_S{session}_COPE_MNIstd_TxGroup{Tx}_avg'

# cmd = [None]
# cmd[0] = f'fslmaths {avg_niftis_path}_v2.nii.gz -thr 3.1 {avg_niftis_path}_thr_v2.nii.gz'
# q.exec_cmds(cmd)


# %% Plot abs value differences (post- minus pre-TX) in ROI-whole brain correlation (COPEs)
"""
NOTE: These plots show areas of brain (group avg) with greatest change in ROI-whole brain correlation, 
not negative vs. positive correlation
>>> Need a different figure to show areas of positive vs. negative correlation

# NOTE: z-scored maps show how extreme a value is compared to the rest of the distribution
>>> here, can be useful for showing which regions have more extreme correlations with the ROI
>>> however, don't show statistical significance

# NOTE: Faith and Lindsay want to see only regions with statistically significant changes in correlation with ROI
>>> Also want to see regions with statistically significant correlations with ROI at individual timepoints?
>>> need to threshold using a p-value

NOTE: BandTogether = 0; WORDS! = 1
"""

threshold = 2  # Define threshold value (if z-scoring)
higherlev_dir = '/Volumes/EVO_Estia/EVO_rest_higherlev_vol' # where avg COPE dir is; destination for figures
rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
for roi in rois:

    # Load avg COPE maps for both groups and time points
    group_map0_t1 = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S1_COPE_MNIstd_TxGroup0_avg.nii.gz')
    map0_t1 = group_map0_t1.get_fdata()
    group_map0_t2 = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S2_COPE_MNIstd_TxGroup0_avg.nii.gz')
    map0_t2 = group_map0_t2.get_fdata()
    group_map1_t1 = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S1_COPE_MNIstd_TxGroup1_avg.nii.gz')
    map1_t1 = group_map1_t1.get_fdata()
    group_map1_t2 = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S2_COPE_MNIstd_TxGroup1_avg.nii.gz')
    map1_t2 = group_map1_t2.get_fdata()

    # Load standard brain for plotting thresholded z-scores
    std_brain_obj = nib.load(MNI_std_path)
    std_brain = std_brain_obj.get_fdata()
    std_brain = np.rot90(std_brain[:,:,40])

    fig, ax = plt.subplots(1, 2, figsize=(10, 5)) # plot (correlation change between pre- vs. post-Tx timepoint) maps in same figure

    # Choose an axial slice to display (axial is in dimension 3 of these arrays); subtract pre- from post-Tx
    # diff_img0 = np.rot90(abs(map0_t2[:,:,40]) - abs(map0_t1[:,:,40])) # plot differences between absolute value COPEs
    # diff_img1 = np.rot90(abs(map1_t2[:,:,40]) - abs(map1_t1[:,:,40]))
    # diff_img0 = np.rot90(abs(abs(map0_t2[:,:,40]) - abs(map0_t1[:,:,40]))) # plot absolute value of differences between absolute value COPEs
    # diff_img1 = np.rot90(abs(abs(map1_t2[:,:,40]) - abs(map1_t1[:,:,40])))
    # diff_img0 = np.rot90(np.square(map0_t2[:,:,40]) - np.square(map0_t1[:,:,40])) # plot difference of squares (squared post- minus squared pre-Tx)
    # diff_img1 = np.rot90(np.square(map1_t2[:,:,40]) - np.square(map1_t1[:,:,40]))
    diff_img0 = np.rot90(z_score(map0_t2[:,:,40]) - z_score(map0_t1[:,:,40])) # plot difference between z-scored COPEs
    diff_img1 = np.rot90(z_score(map1_t2[:,:,40]) - z_score(map1_t1[:,:,40]))

    # Create masked versions (everywhere the image == 0 is just not plotted and will appear black)
    # masked_img0 = np.ma.masked_where(diff_img0 == 0, diff_img0)
    # masked_img1 = np.ma.masked_where(diff_img1 == 0, diff_img1)
    diff_img0 = np.ma.masked_where(diff_img0 == 0, diff_img0)
    diff_img1 = np.ma.masked_where(diff_img1 == 0, diff_img1)

    # Thresholding (if z-scoring)
    masked_img0 = np.ma.masked_where(np.abs(diff_img0) < threshold, diff_img0)
    masked_img1 = np.ma.masked_where(np.abs(diff_img1) < threshold, diff_img1)

    # Determine the common color scale across both images
    vmin = min(np.min(masked_img0), np.min(masked_img1))
    vmax = max(np.max(masked_img0), np.max(masked_img1))

    # Plot standard brain as the background
    ax[0].imshow(std_brain, cmap='gray', interpolation='nearest')
    ax[1].imshow(std_brain, cmap='gray', interpolation='nearest')

    # Create a custom colormap that maps zero values to transparent (if plotting z-scores over MNI152 brain)
    cmap = plt.get_cmap('hot')
    cmap.set_bad(color='black', alpha=0)

    cmap = plt.get_cmap('hot') # set colormap theme
    # cmap.set_bad(color='black')  # set the color for masked values to black

    # Plot WORDS! (group 1) time difference
    ax0 = ax[0].imshow(masked_img0, cmap=cmap, interpolation='nearest', vmin=vmin, vmax=vmax)
    cb = plt.colorbar(ax0, ax=ax[0])  # associate the colorbar with the first axis
    cb.set_label('z-scored post- minus z-scored pre-Tx, threshold=2')
    ax[0].set_title(f'WORDS! Pre- to Post-Tx Change: {roi}')
    ax[0].axis('off')

    # Plot BandTogether (group 0) time difference
    ax1 = ax[1].imshow(masked_img1, cmap=cmap, interpolation='nearest', vmin=vmin, vmax=vmax)
    cb = plt.colorbar(ax1, ax=ax[1])  # associate the colorbar with the second axis
    cb.set_label('z-scored post- minus z-scored pre-Tx, threshold=2')
    ax[1].set_title(f'BandTogether Pre- to Post-Tx Change: {roi}')
    ax[1].axis('off')

    plt.tight_layout()
    plt.show()
    # fig.savefig(f'{higherlev_dir}/{roi}_avgCOPE_Txgroups_diffofsquares.png')
    fig.savefig(f'{higherlev_dir}/{roi}_avgCOPE_Txgroups_zscored_thr=2.png')


# %% Plot individual maps
# NOTE: BandTogether = 0; WORDS! = 1
# roi = 'R_MFG'
# group_map1_t1 = nib.load(f'/Volumes/EVO_Estia/EVO_rest_higherlev_vol/{roi}/{roi}_S1_COPE_MNIstd_TxGroup0_avg.nii.gz')
map = nib.load(f'/Volumes/EVO_Estia/EVO_rest_higherlev_vol/avg_COPEs/{roi}_S1_COPE_MNIstd_TxGroup0_avg.nii.gz')
map = map.get_fdata()

# std_mask = nib.load(f'/Users/holland_brown_ra/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz')
# std_mask = std_mask.get_fdata()
# std_mask[std_mask != 0] = 1

fig, ax = plt.subplots(1, 1, figsize=(5, 5))

# Plot WORDS! (group 1) time difference
img = np.rot90(abs(map[:,:,40]))
ax0 = ax.imshow(img, cmap='hot', interpolation='nearest')
cb = plt.colorbar(ax0)
cb.set_label('COPE values')
ax.set_title(f'BandTogether group avg baseline, {roi}-to-whole brain')
ax.axis('off')

plt.tight_layout()
plt.show()

# %% Plot individual COPE maps
# NOTE: BandTogether = 0; WORDS! = 1
# roi = 'L_MFG'
# img = nib.load(f'/Volumes/EVO_Estia/EVO_rest_higherlev_vol/{roi}/{roi}_S2_TxGroup1_p=-1.nii.gz')
# map1_t1 = group_map1_t1.get_fdata()

# fig, ax = plt.subplots(1, 1, figsize=(5, 5))

# # Plot WORDS! (group 1) time difference
# img = np.rot90(abs(img[:,:,90]))
# ax0 = ax.imshow(img, cmap='hot', interpolation='nearest')
# cb = plt.colorbar(ax0)
# cb.set_label('thresholded cluster z-stat values')
# ax.set_title(f'BandTogether group avg post-Tx, {roi}-to-whole brain')
# ax.axis('off')

# plt.tight_layout()
# plt.show()

# %%

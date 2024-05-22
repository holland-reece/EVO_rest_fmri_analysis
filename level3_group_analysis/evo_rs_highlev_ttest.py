# EVO Post-MEP Resting-State Higher-Level: statistical tests for significance thresholded maps

# Holland Brown

# Updated 2024-04-30
# Created 2024-04-30

# NOTE: BandTogether = 0; WORDS! = 1

# -----------------------------------------------------------------------------------------------
# %%
import csv
import glob
import numpy as np
# import scipy.stats as stats
import nibabel as nib
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import mixedlm

from my_imaging_tools import fmri_tools # class for handling directory structs, handing commands to system, etc.



# Set up paths
# home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to subject directories where lower-level Feat results are
# MNI_std_path = f'/home/holland/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
# Txlabels_csv = '/media/holland/EVO_Estia/EVO_rest_higherlev_vol/EVO_Tx_groups.csv'

home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized' # path to subject directories
higherlev_dir = '/Volumes/EVO_Estia/EVO_rest_higherlev_vol' # where avg COPE dir is; destination for figures
MNI_std_path = f'/Users/holland_brown_ra/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
Txlabels_csv = '/Volumes/EVO_Estia/EVO_rest_higherlev_vol/EVO_Tx_groups.csv'

sessions = ['1','2']
# rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
rois = ['R_MFG'] # test
sites = ['NKI','UW'] # collection sites (also names of dirs)

# read in treatment labels from CSV
with open(Txlabels_csv, mode ='r')as file:
    TxGroups = csv.reader(file)
    group_labels = []
    for line in TxGroups:
        group_labels.append(line)
        print(line)

# %% t-test
"""
NOTE: t-test is suitable if you are comparing two groups or conditions only (e.g., pre-treatment vs. post-treatment).
The t-test will tell you if the means of two groups are statistically different from each other.

>>> Independent t-test: Use this if you have different subjects in each group.
>>> Paired t-test: Use this if the same subjects are measured under both conditions (e.g., before and after treatment).

>>> ideal for comparing timepoints within one treatment group, but not comparing treatment groups to each other
>>> Here, to compare timepoints within the same Tx group, use Paired t-test

"""

# rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
# for roi in rois:

#     # Load avg COPE maps for both groups and time points
#     group0_pre = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S1_COPE_MNIstd_TxGroup0_avg.nii.gz')
#     group0_pre = group0_pre.get_fdata()
#     group0_post = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S2_COPE_MNIstd_TxGroup0_avg.nii.gz')
#     group0_post = group0_post.get_fdata()
#     group1_pre = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S1_COPE_MNIstd_TxGroup1_avg.nii.gz')
#     group1_pre = group1_pre.get_fdata()
#     group1_post = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S2_COPE_MNIstd_TxGroup1_avg.nii.gz')
#     group1_post = group1_post.get_fdata()

#     # These should be arrays of the same shape, with each element representing a pixel/voxel
#     pre_treatment = np.random.normal(loc=100, scale=10, size=100)
#     post_treatment = pre_treatment + np.random.normal(loc=5, scale=2, size=100)  # post-treatment is slightly increased

#     # Perform a paired t-test
#     t_stat, p_values = stats.ttest_rel(pre_treatment, post_treatment)

#     print("T-statistic:", t_stat)
#     print("P-value:", p_values)


# %% Two-way Mixed-effects ANOVA
"""
NOTE: This test can handle one between-subjects factor (treatment group) and one within-subjects factor (time)

Will show:
>>> main effect of the treatment group
>>> main effect of time
>>> interaction effect between treatment group and time

"""

roi = 'R_MFG' # run one ROI at a time
treatment = []

for site in sites:
    datadir = f'{home_dir}/{site}' # where subject dirs are located
    q = fmri_tools(datadir) # get subject IDs list, init functions, etc.
    cope = np.zeros(len(q.subs),)
    for session in sessions:
        for sub in q.subs:
            for label_pair in group_labels:
                if label_pair[0] == sub: # label_pair is a pair containing subject ID and treatment group
                    treatment.append(label_pair[1]) # get treatment group label for this subject

            feat_file_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/cope1.nii.gz'
            group0_pre = nib.load(f'{higherlev_dir}/avg_COPEs/{roi}_S1_COPE_MNIstd_TxGroup0_avg.nii.gz')
            group0_pre = group0_pre.get_fdata()
            

# Create a sample DataFrame
data = pd.DataFrame({
    'subject_id': np.asarray(q.subs),
    'treatment': np.asarray(treatment),
    'time': np.tile(['Pre', 'Post'], 20),
    'cope': np.random.normal(0, 1, 40)  # Simulate some data
})

# Fit a mixed model ANOVA
model = mixedlm("cope ~ treatment*time", data, groups=data["subject_id"], re_formula="~time")
result = model.fit()

print(result.summary())

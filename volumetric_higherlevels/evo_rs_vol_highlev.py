# EVO Post-MEP Resting-State Higher-Level Mixed Effects Linear Model Using Python statsmodels

# Holland Brown

# Updated 2024-04-04
# Created 2024-03-20

# NOTE: 2024-03-29 kernel crashes; see GitHub bug report >> https://github.com/microsoft/vscode-jupyter/wiki/Kernel-crashes
    # 2024-04-03 created new environment (evo-fmri) and installed numpy, nibabel, statsmodels, and pandas fresh


# %%
import os
import numpy as np
import pandas as pd
import nibabel as nib
import statsmodels.api as sm
import statsmodels.formula.api as smf
from my_imaging_tools import fmri_tools
import csv


def create_mixed_effects_model(connectivity_data_session1, connectivity_data_session2, treatment_labels):
    # Convert inputs to numpy arrays if they are not already
    connectivity_data_session1 = np.array(connectivity_data_session1)
    connectivity_data_session2 = np.array(connectivity_data_session2)

    # Create a DataFrame for the model
    df = pd.DataFrame({
        'Session1_Connectivity': connectivity_data_session1.flatten(),
        'Session2_Connectivity': connectivity_data_session2.flatten(),
        'Treatment': treatment_labels * connectivity_data_session1.shape[0]  # Repeat each treatment label for each subject
    })

    # Fit the mixed effects model
    formula = 'Session2_Connectivity ~ Session1_Connectivity + Treatment'
    model = smf.mixedlm(formula, df, groups=df.index)
    result = model.fit()

    return result




# Set up
home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
runs = ['1']
# rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
rois = ['L_MFG'] # test
sites = ['NKI','UW'] # collection sites (also names of dirs)
num_subjects = 55



# %% Exclude all subjects that don't have both sessions from higher levels
# # NOTE: Also manually move subject dirs that were flagged for bad anatomical scans or incidental findings (see spreadsheet)

# cmd = [None]
# for site in sites:
#     datadir = f'{home_dir}/{site}' # where subject dirs are located
#     q = fmri_tools(datadir)
#     for sub in q.subs: # test
#         if os.path.isfile(f'{datadir}/{sub}/func/unprocessed/rest/session_2/run_1/Rest_S2_R1_E1.nii.gz')==False:
#             print(f'{sub}\n')
#             cmd[0] = f'mv {datadir}/{sub} /media/holland/EVO_Estia/EVO_MRI/EXCLUDE_rest_higherlevels'
#             q.exec_cmds(cmd)

# %% TEST: check number of volumes for all participants
dir = f'{home_dir}/UW'
q = fmri_tools(dir)
cmd = [None]*2
for sub in q.subs:
    cmd[0] = f'fslnvols {dir}/{sub}/func/unprocessed/rest/session_1/run_1/Rest_S1_R1_E1.nii.gz'
    cmd[1] = f'fslnvols {dir}/{sub}/func/unprocessed/rest/session_2/run_1/Rest_S2_R1_E1.nii.gz'
    q.exec_cmds(cmd)


# %% Read in Tx group list CSV file
with open('/home/holland/Desktop/EVO_Tx_groups.csv', mode ='r')as file:
    TxGroups = csv.reader(file)
    group_labels = []
    for line in TxGroups:
        group_labels.append(line)
        print(line)

# %% Use lower level COPE files as columns of connectivity matrices for each session and ROI
TxLabels = []
matrix = np.zeros((902629,55)) # for each subject, will reshape NIFTI into a vector -> 1 column
# matrix = np.zeros(91,109,91,num_subjects)

for roi in rois:
    for session in sessions:
        matrix = np.zeros((902629,51)) # number of voxels by number of participants
        i = 0 # init counter (for indexing final output matrix)
        for site in sites:
            datadir = f'{home_dir}/{site}' # where subject dirs are located

            # for each subject in group_labels list: save group label, normalize COPE, and save COPE as col of matrix
            for label_pair in group_labels:
                # label_pair is a pair containing subject ID and treatment group
                sub = label_pair[0]
                Tx = label_pair[1]
                # cope_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/rendered_thresh_zstat1.nii.gz'
                cope_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/cope1.nii.gz'


                # check that FSL Feat stats dir exists
                if os.path.exists(cope_path):
                    if session == '1' and roi == rois[0]: # only save treatment label for each subject once
                        TxLabels.append(Tx) # save Tx labels in a list, but only once per subject

                    # load and flatten COPE data into a vector
                    nii = nib.load(cope_path) # read in NIFTI file
                    data = nii.get_fdata() # reshape into vector (length: total number of voxels)
                    
                    # normalize COPE distribution so its magnitude is 1 (divide by l2 norm) -> puts all vectors on same scale
                    # l2_norm = np.linalg.norm(data)
                    # data_norm = data / l2_norm
                    # if np.sum(data_norm) == 0: # check that vector is not all zeros
                    #     print(f'{sub}, {roi}, S{session} has 0 sum...')

                    # data_norm.tofile(norm_fn, sep=',') # save normalized vector
                    matrix[:,i] = data.transpose() # append to input matrix
                    i += 1 # update counter
                else:
                    if (sub[0]=='9' and site=='NKI') or (sub[0]=='W' and site=='UW'):
                        print(f'Does not exist:\n\t{cope_path}\n')

        if session == '1':
            matrix1 = np.array(matrix)
            matrix_fn = f'/home/holland/Desktop/{roi}_S{session}_rest_thresh_zstat.csv'
            matrix1.tofile(matrix_fn, sep=',')
        elif session == '2':
            matrix2 = np.array(matrix)
            matrix_fn = f'/home/holland/Desktop/{roi}_S{session}_rest_thresh_zstat.csv'
            matrix2.tofile(matrix_fn, sep=',')

# %% Calculate difference between correlations S1 and S2 for each subject
# NOTE: BandTogether = 0; WORDS! = 1
import matplotlib.pyplot as plt

ix_tx0 = (np.array(TxLabels) == '0') # Boolean vector -> use as index
delta_tx0 = matrix2[..., ix_tx0].mean(-1) - matrix1[..., ix_tx0].mean(-1) # time 2 - time 1 for BandTogether
delta_tx1 = matrix2[..., ~ix_tx0].mean(-1) - matrix1[..., ~ix_tx0].mean(-1) # time 2 - time 1 for WORDS!
delta_tx = delta_tx0 - delta_tx1 # difference between Tx groups
plt.scatter(np.arange(100), delta_tx[delta_tx.argsort()][-100:][::-1]) # space x axis evenly; sort differences by magnitude
# plt.plot(np.linspace(-6, 8, 100), np.linspace(-6, 8, 100))
plt.show()


# %% Load CSV connectivity matrices
# chunk_size = 1000

# matrix1 = pd.read_csv(f'/home/holland/Desktop/L_MFG_S1_rest_higherlev_copes.csv')
# print("Done reading session 1 CSV.")
# matrix2 = pd.read_csv(f'/home/holland/Desktop/L_MFG_S2_rest_higherlev_copes.csv')
# print("Done reading session 2 CSV.")
print(np.shape(matrix1))
print(np.shape(matrix1))
print(len(TxLabels))


# %% Run model
# model_result = create_mixed_effects_model(connectivity_data_session1, connectivity_data_session2, treatment_labels)
# print(model_result.summary())

# NOTE: session 2 is the dependent variable; we want to see if session 1 and Tx group have any effect on it
# results = create_mixed_effects_model(matrix1,matrix2,TxLabels)
# print(results.summary())

# %% TEST: Model
# Convert inputs to numpy arrays if they are not already
# connectivity_data_session1 = matrix1
# connectivity_data_session2 = matrix2

# # Create a DataFrame for the model
# df = pd.DataFrame({
#     'Session1_Connectivity': connectivity_data_session1.flatten(),
#     'Session2_Connectivity': connectivity_data_session2.flatten(),
#     'Treatment': TxLabels * connectivity_data_session1.shape[0]  # Repeat each treatment label for each subject
# })


# # %% Fit the mixed effects model
# formula = 'Session2_Connectivity ~ Session1_Connectivity + Treatment'
# model = smf.mixedlm(formula, df, groups=df.index)
# result = model.fit()



# EVO Post-MEP Resting-State Higher-Level Mixed Effects Linear Model Using Python statsmodels

# Holland Brown

# Updated 2024-03-29
# Created 2024-03-20



# %
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

    # Ensure that the data shapes are compatible
    if connectivity_data_session1.shape[1] != connectivity_data_session2.shape[1] or \
       connectivity_data_session1.shape[1] != len(treatment_labels):
        raise ValueError("Number of participants in connectivity data does not match the number of treatment labels.")

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

# Example usage:
# Assume connectivity_data_session1 and connectivity_data_session2 are numpy arrays,
# and treatment_labels is a list of strings.
# model_result = create_mixed_effects_model(connectivity_data_session1, connectivity_data_session2, treatment_labels)
# print(model_result.summary())




# % Set up

home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
runs = ['1']
# rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
rois = ['L_MFG'] # test
sites = ['NKI','UW'] # collection sites (also names of dirs)
num_subjects = 55



# # %% Exclude all subjects that don't have both sessions from higher levels
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

# % Read in Tx group list CSV file
with open('/home/holland/Desktop/EVO_Tx_groups.csv', mode ='r')as file:
    TxGroups = csv.reader(file)
    group_labels = []
    for line in TxGroups:
        group_labels.append(line)
        print(line)

# % Use lower level COPE files as columns of connectivity matrices for each session and ROI
TxLabels = []
matrix = np.zeros((902629,55)) # number of voxels by number of participants
j = 0

for roi in rois:
    for session in sessions:
        j += 1
        i = 0 # init counter (for indexing final output matrix)
        for site in sites:
            datadir = f'{home_dir}/{site}' # where subject dirs are located
            q = fmri_tools(datadir)

            # list is a pair containing subject ID and treatment group
            for list in group_labels:
                sub = list[0]
                Tx = list[1]
                
                # print(Tx)
                cope_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/cope1.nii.gz'
                # if os.path.isfile(cope_path)==False:
                #     print(f'\n{sub} has no lower level S{session} {roi} COPE file.\n')
                # else:
                if j == 1:
                    TxLabels.append(Tx) # save Tx labels in a list, but only once per subject
                norm_fn = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/{roi}_S{session}_cope1_normalized.nii.gz'
                if os.path.isfile(norm_fn)==False:
                    nii = nib.load(cope_path) # read in NIFTI file
                    data = nii.get_fdata().flatten()
                    
                    # Normalize COPE distribution
                    l2_norm = np.linalg.norm(data)
                    data_norm = data / l2_norm
                # else:
                #     data_norm = nib.load(norm_fn) # if already exists, load normalized COPE

                # data_norm.tofile(norm_fn, sep=',') # save normalized vector
                    matrix[:,i] = data_norm.transpose() # append to input matrix
                    i += 1 # update counter

            if session == '1':
                matrix1 = np.array(matrix)
                matrix_fn = f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}_S{session}_rest_higherlev_copes.csv'
                matrix1.tofile(matrix_fn, sep=',')
            elif session == '2':
                matrix2 = np.array(matrix)
                matrix_fn = f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/{roi}_S{session}_rest_higherlev_copes.csv'
                matrix2.tofile(matrix_fn, sep=',')



# # %% Load CSV connectivity matrices

# session1 = pd.read_csv(f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/L_MFG_S1_rest_higherlev_copes.csv')
# session2 = pd.read_csv(f'/media/holland/EVO_Estia/EVO_rest_higherlev_vol/L_MFG_S2_rest_higherlev_copes.csv')
print(np.shape(matrix1))
print(np.shape(matrix1))
print(len(TxLabels))


# % Run model
# NOTE: session 2 is the dependent variable; we want to see if session 1 and Tx group have any effect on it
results = create_mixed_effects_model(matrix1,matrix2,TxLabels)
print(results.summary())
# %%

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


# def create_mixed_effects_model(connectivity_data_session1, connectivity_data_session2, treatment_labels):
#     # Convert inputs to numpy arrays if they are not already
#     connectivity_data_session1 = np.array(connectivity_data_session1)
#     connectivity_data_session2 = np.array(connectivity_data_session2)

#     # Create a DataFrame for the model
#     df = pd.DataFrame({
#         'Session1_Connectivity': connectivity_data_session1.flatten(),
#         'Session2_Connectivity': connectivity_data_session2.flatten(),
#         'Treatment': treatment_labels * connectivity_data_session1.shape[0]  # Repeat each treatment label for each subject
#     })

#     # Fit the mixed effects model
#     formula = 'Session2_Connectivity ~ Session1_Connectivity + Treatment'
#     model = smf.mixedlm(formula, df, groups=df.index)
#     result = model.fit()

    # return result

def matrix_to_df(matrix, group, time):
    df = pd.DataFrame(matrix)
    df = df.stack().reset_index()
    df.columns = ['Measurement', 'Subject', 'Value']
    df['Time'] = time
    df['Group'] = group
    return df

# Flatten the matrices and create a DataFrame
# def flatten_data(matrix, group, time):
#     # Flatten the matrix and turn it into a DataFrame
#     subjects, x, y = matrix.shape
#     df = pd.DataFrame(matrix.reshape(subjects, x*y).T, 
#                       columns=[f'subject_{i+1}' for i in range(subjects)])
#     df['Time'] = time
#     df['Group'] = group
#     df = df.melt(id_vars=['Time', 'Group'], var_name='Subject', value_name='Value')
#     return df


# Set up
# home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc
home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
runs = ['1']
# rois = ['R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
rois = ['L_MFG'] # test
sites = ['NKI','UW'] # collection sites (also names of dirs)
num_subjects = 51 # number of subjects we want to include in higher levels



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
dir = f'{home_dir}/NKI'
q = fmri_tools(dir)
cmd = [None]*2
for sub in q.subs:
    cmd[0] = f'fslnvols {dir}/{sub}/func/unprocessed/rest/session_1/run_1/Rest_S1_R1_E1.nii.gz'
    cmd[1] = f'fslnvols {dir}/{sub}/func/unprocessed/rest/session_2/run_1/Rest_S2_R1_E1.nii.gz'
    q.exec_cmds(cmd)


# %% Read in Tx group list CSV file
with open('/Volumes/EVO_Estia/EVO_rest_higherlev_vol/EVO_Tx_groups.csv', mode ='r')as file:
    TxGroups = csv.reader(file)
    group_labels = []
    for line in TxGroups:
        group_labels.append(line)
        print(line)

# %% Use lower level COPE files as columns of connectivity matrices for each session and ROI
TxLabels = []
# matrix = np.zeros((902629,55)) # for each subject, will reshape NIFTI into a vector -> 1 column
# matrix = np.zeros(91,109,91,num_subjects)

for roi in rois:
    for session in sessions:
        matrix = np.zeros((902629,num_subjects)) # number of voxels by number of participants
        # sum_mat = np.zeros((91,109,91)) # will use this for means later
        i = 0 # init counter (for indexing final output matrix)
        for site in sites:
            datadir = f'{home_dir}/{site}' # where subject dirs are located

            # for each subject in group_labels list: save group label, normalize COPE, and save COPE as col of matrix
            for label_pair in group_labels:
                # label_pair is a pair containing subject ID and treatment group
                sub = label_pair[0]
                Tx = label_pair[1]
                cope_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/zstat1.nii.gz'
                # cope_path = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R1_lowerlev_vol.feat/stats/cope1.nii.gz'


                # check that FSL Feat stats dir exists
                if os.path.exists(cope_path):
                    if session == '1' and roi == rois[0]: # only save treatment label for each subject once
                        TxLabels.append(Tx) # save Tx labels in a list, but only once per subject

                    # load and flatten COPE data into a vector
                    nii = nib.load(cope_path) # read in NIFTI file
                    data = nii.get_fdata() # get subject's lower-level result as numpy array
                    print(f'{sub} {session} {np.shape(data)}')
                    # sum_mat += data # add subject's lower-level result to sum

                    vector = data.flatten() # reshape into vector (length: total number of voxels)
                    matrix[:,i] = vector.transpose() # save column vector to matrix
                    i += 1 # update counter
                else:
                    if (sub[0]=='9' and site=='NKI') or (sub[0]=='W' and site=='UW'):
                        print(f'Does not exist:\n\t{cope_path}\n')
                

        if session == '1':
            matrix1 = np.array(matrix)
            matrix_fn = f'/Users/holland_brown_ra/Desktop/{roi}_S{session}_rest_zstat.csv'
            matrix1.tofile(matrix_fn, sep=',')

            # mean_mat1 = np.array(sum_mat) * (1/num_subjects) # mean for this session
            # meanmat_fn = f'/Users/holland_brown_ra/Desktop/{roi}_S{session}_rest_zstat_mean.csv'
            # mean_mat1.tofile(meanmat_fn, sep=',')

        elif session == '2':
            matrix2 = np.array(matrix)
            matrix_fn = f'/Users/holland_brown_ra/Desktop/{roi}_S{session}_rest_thresh_zstat.csv'
            matrix2.tofile(matrix_fn, sep=',')

            # mean_mat2 = np.array(sum_mat) * (1/num_subjects) # mean for this session
            # meanmat_fn = f'/Users/holland_brown_ra/Desktop/{roi}_S{session}_rest_zstat_mean.csv'
            # mean_mat2.tofile(meanmat_fn, sep=',')

# %% Calculate difference between correlations S1 and S2 for each subject
# NOTE: BandTogether = 0; WORDS! = 1
import matplotlib.pyplot as plt

ix_tx0 = (np.array(TxLabels) == '0') # Boolean vector -> use as index
delta_tx0 = matrix2[..., ix_tx0].mean(-1) - matrix1[..., ix_tx0].mean(-1) # time 2 - time 1 for BandTogether
delta_tx1 = matrix2[..., ~ix_tx0].mean(-1) - matrix1[..., ~ix_tx0].mean(-1) # time 2 - time 1 for WORDS!
delta_tx = delta_tx0 - delta_tx1 # difference between Tx groups

colors = np.arange(100)  # gradient of colors based on x-axis index values
plt.scatter(np.arange(100), delta_tx[delta_tx.argsort()][-100:][::-1], s=15, c=colors, cmap='viridis') # space x axis evenly; sort differences by magnitude
# plt.plot(np.linspace(-6, 8, 100), np.linspace(-6, 8, 100))

plt.xlabel('Index') # arbitrary index, just to make them equally spaced along x
plt.ylabel(f'ROI-to-whole brain thresholded z-score change\n(BandTogether minus WORDS!)') # y shows the difference between Tx groups' time1-time2 differences

roi_string = 'Left Middle Frontal Gyrus' # how you want ROI name to appear in the caption and title
# caption = f'Here, higher values on the y-axis represent voxels where \npre-post-treatment change are most different\n between the BandTogether and WORDS!\n treatment groups in the {roi_string}.'
# plt.text(50, -4, caption, ha='center')
plt.title(f'{roi_string}-to-wholebrain functional activity change: BandTogether vs. WORDS!') # Title for the plot


plt.show()

# %% Get map that shows the same thing as above (differences between time 1 and time 2 between groups), but as a brain map



# %% Load CSV connectivity matrices: THIS DOESN'T WORK
# NOTE: haven't been able to successfully load these CSV files; not sure why - too big?
# chunk_size = 1000

# matrix1 = pd.read_csv(f'/home/holland/Desktop/L_MFG_S1_rest_higherlev_copes.csv')
# print("Done reading session 1 CSV.")
# matrix2 = pd.read_csv(f'/home/holland/Desktop/L_MFG_S2_rest_higherlev_copes.csv')
# print("Done reading session 2 CSV.")
print(np.shape(matrix1))
print(np.shape(matrix2))
print(len(TxLabels))


# %% Run model
# NOTE: session 2 is the dependent variable; we want to see if session 1 and Tx group have any effect on it
TxLabels_int = np.array([int(val) for val in TxLabels]) # convert labels list to integer vector
ix_tx0 = (np.array(TxLabels) == '0') # Boolean vector -> use as index
band_time1 = matrix1[..., ix_tx0] # BandTogether mean session 1
band_time2 = matrix2[..., ix_tx0] # BandTogether mean session 2
words_time1 = matrix1[..., ~ix_tx0] # WORDS! mean session 1
words_time2 = matrix2[..., ~ix_tx0] # WORDS! mean session 2

# Combine the data
df = pd.concat([
    matrix_to_df(band_time1, 'BandTogether', 'time1'),
    matrix_to_df(band_time2, 'BandTogether', 'time2'),
    matrix_to_df(words_time1, 'WORDS!', 'time1'),
    matrix_to_df(words_time2, 'WORDS!', 'time2')
])

# Reset the subject identifier to be unique across groups if necessary (helps account for subject variance)
df['Subject'] = df['Group'] + '_S' + df['Subject'].astype(str)

# Mixed Effects Model: Value ~ Time + Group + Time:Group
model = smf.mixedlm("Value ~ Time * Group", df, groups=df["Subject"], re_formula="~Time")
result = model.fit()

print(result.summary())

# %% Plot results of model
import matplotlib.pyplot as plt
import seaborn as sns

# (1) see how well model fits the data ------------------------------------
# Calculate fitted values from the model
df['Fitted'] = result.fittedvalues

# Plotting observed vs. fitted values
plt.figure(figsize=(10, 6))
sns.scatterplot(x=df['Value'], y=df['Fitted'], hue=df['Group'], style=df['Time'])
plt.plot([df['Value'].min(), df['Value'].max()], [df['Value'].min(), df['Value'].max()], 'r--')  # Line of perfect fit
plt.xlabel('Observed Values')
plt.ylabel('Fitted Values')
plt.title('Observed vs. Fitted Values')
plt.show()

# %% (2) Plot residuals to check the assumption of homoscedasticity and normality in residuals -----------------------
# NOTE: homoscedasticity is the condition in which variance of the residuals is consistent
# (2) Calculate residuals
df['Residuals'] = result.resid

plt.figure(figsize=(10, 6))
sns.scatterplot(x=result.fittedvalues, y=result.resid, hue=df['Group'])
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Fitted Values')
plt.ylabel('Residuals')
plt.title('Residuals vs. Fitted Values')
plt.show()

# %% (3) Create plots of fixed effects (time and group) and effect of their interactions ----------------------------------
# Using seaborn to create interaction plots
plt.figure(figsize=(12, 8))
sns.lineplot(data=df, x='Time', y='Value', hue='Group', style='Group', markers=True, dashes=False)
plt.title('Interaction of Time and Group on Response')
plt.show()

# %% (4) Random effects due to subject variability ----------------------------------
# Extract random effects
re_frame = result.random_effects

# Convert the random effects dictionary to DataFrame
re_df = pd.DataFrame({k: v.values.flatten() for k, v in re_frame.items()}).T
re_df.columns = ['Intercept', 'Slope']

# Plot the random intercepts and slopes
plt.figure(figsize=(12, 6))
sns.histplot(re_df['Intercept'], kde=True, color='blue', label='Intercept')
sns.histplot(re_df['Slope'], kde=True, color='green', label='Slope')
plt.title('Distribution of Random Effects')
plt.legend()
plt.show()


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



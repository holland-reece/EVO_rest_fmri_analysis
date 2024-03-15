# Visualizing EVO Post-MEP Resting-State Lower-Level Mixed Effects Linear Model Using FSL Feat

# Holland Brown

# Updated 2023-03-15
# Created 2024-03-15

# NOTE: numpy can't read NIFTIs; use nibabel to read in ROI masks for carpet plots

# --------------------------------------------------------------------------------------
# %%
import os
import subprocess
import numpy as np
# import glob
import matplotlib.pyplot as plt
from my_imaging_tools import fmri_tools

# Important dirs
home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
runs = ['1']
rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
sites = ['NKI','UW'] # collection sites (also names of dirs)
# rois = ['L_rACC','R_rACC']

# %% Functions

# Read a single-column text file containing ROI activation time series data
def read_activation_file(filepath):
    return np.loadtxt(filepath)

def plot_carpet_plot(data, title, ax):
    """
    Plot a carpet plot of ROI activation time series data!
    """
    ax.imshow(data, aspect='auto', cmap='jet')
    ax.set_title(title)
    ax.set_ylabel('ROI')
    ax.set_xlabel('Time')

def plot_activations(directory_path, figfilename):
    """
    Process a single directory, plotting carpet plots for each file and returning the average activations
    """
    activations = []
    fig, axs = plt.subplots(nrows=len(os.listdir(directory_path)), ncols=1, figsize=(10, 3 * len(os.listdir(directory_path))))
    
    if len(os.listdir(directory_path)) == 1:
        axs = [axs]
    
    for i, filename in enumerate(os.listdir(directory_path)):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory_path, filename)
            activation_data = read_activation_file(filepath)
            activations.append(activation_data)
            plot_carpet_plot(activation_data, filename, axs[i])

            # figpath = os.path.join(directory_path, f'{figfilename}.png')
            plt.savefig(figfilename)
            plt.close()
    
    # plt.tight_layout()
    # plt.show()
    
    return np.mean(activations, axis=0)

def plot_average_activations(directories, fig_fullpath):
    """
    Plot the average ROI activations from each directory in a single plot
    """
    average_activations = []
    labels = []
    
    for directory_path in directories:
        avg_activation = plot_activations(directory_path, fig_fullpath)
        average_activations.append(avg_activation)
        labels.append(os.path.basename(directory_path))
    
    plt.figure(figsize=(10, 6))
    for i, avg_activation in enumerate(average_activations):
        plt.plot(avg_activation, label=labels[i])
    
    plt.title('Average ROI Activations')
    plt.xlabel('Time')
    plt.ylabel('Activation')
    plt.legend()
    # plt.show()
    plt.savefig(f'{fig_fullpath}.png')
    plt.close()

# %% For each subject, plot carpet plots
figure_path = f'{home_dir}/EVO_rest_lower_levels'

dirlist = []
for site in sites:
    datadir = f'{home_dir}/{site}'
    q = fmri_tools(datadir)
    for sub in q.subs:
        for roi in rois:
            for session in sessions:
                for run in runs:
                    featdir = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/S{session}_R{run}_lowerlev_vol.feat'
                    plot_fn = f'{datadir}/{sub}/func/rest/rois/{roi}/rest_lowerlev_vol/'
                    if os.path.isdir(featdir)==False:
                        print(f'{sub} has no {roi} Feat directory.')
                    else:
                        dirlist.append(f'{featdir}')

                plot_average_activations(dirlist, f'{home_dir}/EVO_rest_lower_levels_{roi}_S{session}.png')



                        


# %% Test
subjectdir = f'/Volumes/EVO_Estia/EVO_MRI/organized/NKI/97048/func/rest/rois/L_MFG/rest_lowerlev_vol/L_MFG_S1_R1_denoiseaggrfunc_bin0.8.nii.gz'
# plot_activations(subjectdir, f'/Volumes/EVO_Estia/EVO_MRI/organized/NKI/97048/func/rest/rois/L_MFG/rest_lowerlev_vol/L_MFG_ts_plot.png')
roidata = read_activation_file(subjectdir)
print(roidata)
# %%

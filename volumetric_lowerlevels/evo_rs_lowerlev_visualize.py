# Visualizing EVO Post-MEP Resting-State Lower-Level Mixed Effects Linear Model Using FSL Feat

# Holland Brown

# Updated 2023-03-15
# Created 2024-03-15

# --------------------------------------------------------------------------------------
# %%
import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from my_imaging_tools import fmri_tools

# Important dirs
home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc

# q = fmri_tools(studydir=datadir, subjectlist_text=args.subjecttextlist) # init functions and subject list

sessions = ['1','2']
runs = ['1']
rois = ['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
sites = ['NKI','UW'] # collection sites (also names of dirs)
# rois = ['L_rACC','R_rACC']

# %% Functions

def read_activation_file(filepath):
    """
    Reads a single-column text file containing ROI activation time series data.
    """
    return np.loadtxt(filepath)

def plot_carpet_plot(data, title, ax):
    """
    Plots a carpet plot of ROI activation time series data.
    """
    ax.imshow(data, aspect='auto', cmap='jet')
    ax.set_title(title)
    ax.set_ylabel('ROI')
    ax.set_xlabel('Time')

def process_directory(directory_path):
    """
    Processes a single directory, plotting carpet plots for each file and returning the average activations.
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
    
    plt.tight_layout()
    plt.show()
    
    return np.mean(activations, axis=0)

def plot_average_activations(directories):
    """
    Plots the average ROI activations from each directory in a single plot.
    """
    average_activations = []
    labels = []
    
    for directory_path in directories:
        avg_activation = process_directory(directory_path)
        average_activations.append(avg_activation)
        labels.append(os.path.basename(directory_path))
    
    plt.figure(figsize=(10, 6))
    for i, avg_activation in enumerate(average_activations):
        plt.plot(avg_activation, label=labels[i])
    
    plt.title('Average ROI Activations')
    plt.xlabel('Time')
    plt.ylabel('Activation')
    plt.legend()
    plt.show()

# %%
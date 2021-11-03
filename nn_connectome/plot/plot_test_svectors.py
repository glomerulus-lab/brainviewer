import os
import argparse
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import ListedColormap
from matplotlib import gridspec
import sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
import util.load_mat as load_mat
import palettable # https://jiffyclub.github.io/palettable/





parser = argparse.ArgumentParser(description='Plot dominant factors of connectome solution')
# Arguments
parser.add_argument('solution_name',    type=str, nargs=1, help='Name of .mat solution file, including or excluding file extension.')
parser.add_argument('path_to_solution', type=str, nargs=1, help='Dir path where solution is located')
parser.add_argument('n',                type=str, nargs=1, help='number of factors to plot')
# Flags
parser.add_argument('-greedy', action='store_true', help='Search ../lowrank_connectome/data for solution.')
parser.add_argument('-nneg',    action='store_true', help='Plot reordered & scaled solution, rather than scaled QR decomposition.')

def plot_svectors(U, V, output_name, n, nneg=False):
    '''
    Maps voxel coordinates to show connection patterns for n factors.

    Parameters:
        U (int arr): target shape (nx * r)
        V (int arr): source shape (r * ny)
        testname (str) : 'test'
        output_name (str) : part of outputted file's name
        n (int) : number of factors to create
    Optional parameters:
        nneg (bool) : indicates a nonnegative solution
    '''
    voxel_coords_source, voxel_coords_target = load_mat.load_tvoxel_coords('test')

    if(nneg):
        outputpath = 'plots/nneg/'

        Q1 = U.copy()
        Q2 = (V.T).copy()

        r = Q1.shape[1]
        factor_norms_sq = np.zeros(r)

        for rank in range(r):
            Q1_r = Q1[:, rank]
            Q2_r = Q2[:, rank]
            
            Q2_norm = np.linalg.norm(Q2_r)

            # Calculate magnitude
            factor_norms_sq[rank] = np.linalg.norm(Q1_r) *Q2_norm 

            Q1[:, rank] *= Q2_norm
            Q2[:, rank] /= Q2_norm

        # Sort indices of factor_norms_sq in decsending order
        indexlist = np.argsort(-1*factor_norms_sq)

        # Sort magnitude order least to greatest, sort Q1 and Q2 vectors to match
        factor_norms_sq = factor_norms_sq[indexlist]
        Q1 = Q1[:, indexlist]
        Q2 = Q2[:, indexlist]  
    
    # Pull out top n factors and calculate F matrix
    for j in range(int(n)):
        magnitude = factor_norms_sq[j]
        F = np.outer(Q1[:,j], Q2[:,j].T)

        filename = str(output_name)+'_factor_'+str(j+1)
        plot_factor(Q1[:,j], Q2[:,j], F, filename, magnitude, j+1)

# Visualize the source and target for the given factor.
def plot_factor(target, source, matrix, filename, magnitude, factor):
    '''
    Visualizes the source and target, as well as the matrix of a given factor.

    Parameters:
        target_img (): connectivity of the target
        source_img (): connectivity of the source
        testname (str): 'top_view', 'flatmap'
        filename (str): name of output image file
        magnitude (int): size of factor??
        factor (int): factor number
    '''
    axis_font = {'size':'16'}
    legend_font = {'size':'14'}
    title_font = {'size':'18'}
    plt.rc('xtick',labelsize=14)
    plt.rc('ytick',labelsize=14)
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(13,8))

    # Plot target
    lg = ax[0].plot(np.arange(1,201), target, label="Target", color='black')
    ax[0].axes.set_xlabel("Position", **axis_font)
    ax[0].axes.set_ylabel("Target", **axis_font)

    # Plot source
    ax2 = ax[0].twinx()
    ax2.axes.set_ylabel("Source", **axis_font)
    lg2 = plt.plot(np.arange(1,201), source, label="Source", color='tomato')

    lgs = lg+lg2
    labels = [l.get_label() for l in lgs]
    plt.legend(lgs, labels, loc="best",prop=legend_font, title="Factors:", title_fontsize='large')


    # Plot factor matrix
    imgMin = np.nanmin(matrix)
    imgMax = .77
    colormapLimit = max(np.abs(imgMin), np.abs(imgMax)) * 0.9
    im = ax[1].imshow(matrix, label = "Factor matrix",cmap="Reds")
    ax[1].axes.yaxis.set_visible(False)
    ax[1].axes.xaxis.set_visible(False)
    im.set_clim(0,colormapLimit)
    ax[1].axes.set_title("Factor Matrix",**title_font)

    title_height = 0.92
    title_testname = "Test"
    plt.figtext(0.52,title_height,title_testname + " Factor " + str(factor) + ", Norm: " + "{:.2f}".format(magnitude), ha='center', va='center', fontsize="22")
    plt.savefig(filename.replace(".","_")+".png", bbox_inches='tight', dpi=600)
    plt.clf()
    plt.close()


if __name__ == '__main__':
    args = parser.parse_args()
    U, V = load_mat.load_solution(args.solution_name[0],args.path_to_solution[0], args.greedy)
    plot_svectors(U, V, args.solution_name[0].split('/')[-1], args.n[0], args.nneg)
    
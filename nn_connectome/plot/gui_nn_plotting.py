import os

import argparse
import scipy.io
import numpy as np

import matplotlib.cm
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import ListedColormap
from matplotlib import gridspec

from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import time

import sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
import util.load_mat as load_mat
#import palettable # https://jiffyclub.github.io/palettable/


parser = argparse.ArgumentParser(description='Plot dominant factors of connectome solution')
# Arguments
parser.add_argument('testname',         type=str, nargs=1, help='Name of test to plot. "flatmap" or "top_view"')
parser.add_argument('solution_name',    type=str, nargs=1, help='Name of .mat solution file, including or excluding file extension.')
parser.add_argument('path_to_solution', type=str, nargs=1, help='Dir path where solution is located')
parser.add_argument('n',                type=str, nargs=1, help='number of factors to plot')
# Flags
parser.add_argument('-greedy', action='store_true', help='Search ../lowrank_connectome/data for solution.')
parser.add_argument('-nneg',    action='store_true', help='Plot reordered & scaled solution, rather than scaled QR decomposition.')

#set up tkinter window
window_dim = "500x500"
window = Tk()
window.configure(bg='green')
window.title('Brainviewer')
window.geometry(window_dim)

canvas = Canvas(window, height = 330, width=330, bg="blue")
canvas.pack()
figcanvas = -1

def plot_svectors(U, V, testname, output_name, n, nneg=False):
    '''
    Maps voxel coordinates to show connection patterns for n factors.
    Parameters:
        U (int arr): target shape (nx * r)
        V (int arr): source shape (r * ny)
        testname (str) : 'flatmap' or 'top_view'
        output_name (str) : part of outputted file's name
        n (int) : number of factors to create
    Optional parameters:
        nneg (bool) : indicates a nonnegative solution
    '''
    voxel_coords_source, voxel_coords_target, view_lut = load_mat.load_voxel_coords(testname)

    if(nneg):

        Q1 = U.copy()
        Q2 = (V.T).copy()

        r = Q1.shape[1]
        factor_norms_sq = np.zeros(r)

        for rank in range(r):
            
            Q1_r = Q1[:, rank]
            Q2_r = Q2[:, rank]
            Q2_norm = np.linalg.norm(Q2_r)

            factor_norms_sq[rank] = np.linalg.norm(Q1_r) * Q2_norm 

            Q1[:, rank] *= Q2_norm
            Q2[:, rank] /= Q2_norm

        indexlist = np.argsort(-1*factor_norms_sq)
        Q1 = Q1[:, indexlist]
        Q2 = Q2[:, indexlist]
    else:

        Q1, R1 = np.linalg.qr(U, mode='reduced')
        Q2, R2 = np.linalg.qr(V.T)
        u, S, vh = np.linalg.svd(R1 @ (R2.T) )
        Q1 = Q1 @ u * S
        Q2 = Q2 @ vh.T
        

    #this is how I implemented the pixel coords & col relation -- change to use coords lookup table
    #build pixel lookup table
    pixel_to_index = build_pixel_to_index(Q2.shape[0], voxel_coords_source)
    print(pixel_to_index.shape)
    print("finished building pixel to col index")

    args = [pixel_to_index, Q1, Q2, voxel_coords_target, voxel_coords_source, view_lut, canvas]
    
    get_cursor_position(args)

    
def get_cursor_position(args):
    #window dimensions
    greeting = Label(text="Welcome to BrainviewerUI!")
    greeting.pack()
    
    #on mouse motion within the window, change title to reflect cursor position    
    canvas.bind('<Motion>', lambda event, arg = args: get_cursor_coords(event, arg))
    canvas.bind('<Button-1>', lambda event, arg = args: plot_cursor_coords(event, arg))
    window.bind('r', lambda event, arg = args: reset_image(event, args))
    window.bind('x', close_window)
    window.mainloop()


def reset_image(event, args):
    args[6].destroy()
    args[6] = Canvas(window, height = 330, width=330, bg="blue")
    args[6].pack()

def close_window(event):
    window.destroy()
    
def plot_cursor_coords(event, args):
    cursor_coords = (event.x, event.y)
    #plot the coords
    target_index = args[0][cursor_coords[0]][cursor_coords[1]]
    if target_index != -1:
        plot_connection_strength_for_pixel(cursor_coords, target_index, args[1], args[2], args[3],args[4], args[5], target_index, args[6])
        #canvas.pack()
        
def get_cursor_coords(event, args):
    cursor_coords = (event.x, event.y)
    window.title(cursor_coords)
        
def map_to_grid(image_vec, voxel_coords, view_lut):
    ''' 
    Returns 2D image with the size of view_lut and contents of coordinate mappings for vectorized solution.
    
    Parameters:
        image_vec (): image values
        voxel_coords (): image indices
        view_lut (): image shape
    '''
    #initialize the image to nans
    new_image = np.empty(view_lut.shape)
    new_image[:] = np.nan
    for i in range(image_vec.shape[0]):
        new_image[voxel_coords[i,0], voxel_coords[i,1]] = image_vec[i]
    return new_image


#this method builds the matrix to get column index from pixel coords
def build_pixel_to_index(source_count, source_coords):
    #get the shape for pixel_to_index matrix
    pixel_to_index = np.empty((285, 330), int)
    pixel_to_index[:] = -1
    for i in range(source_count):
        source_voxel = source_coords[i]
        pixel_to_index[source_voxel[1]][source_voxel[0]] = i
    return pixel_to_index
 
def plot_connection_strength_for_pixel(pixel_wanted, desired_index, Q1, Q2, voxel_coords_target,voxel_coords_source, view_lut, pic_name, canvas):
    #give this function a pixel within (0,0) and (285, 330) and it will plot the voxel from that point
        
    #compute W_i for desired index
    W_i = Q1 @ Q2[desired_index,:].T
    print("Desired index: {}".format(desired_index))
    #get the connection strength img
    connection_strength_img = map_to_grid(W_i, voxel_coords_target, view_lut)
    plot_connection_strength_for_col(connection_strength_img, voxel_coords_source, desired_index, pic_name, canvas)
    
def plot_connection_strength_for_col(target_img, source_coords, source_index, img_name, canvas):    
    cmap_view = matplotlib.cm.inferno
    cmap_pixel = matplotlib.cm.cool
    cmap_view.set_bad(alpha=0)
    cmap_pixel.set_bad(alpha=0)

    # plot & params
    fig, ax = plt.subplots(figsize=(4, 4))   
    
    # plot connectivity
    im = plt.pcolormesh(target_img, zorder=1, cmap=cmap_view, vmin=0, vmax = .01)
    
    # plot source voxel
    source_voxel = source_coords[source_index]
    plt.plot(source_voxel[1], source_voxel[0], 'co', markersize=5)    
    plt.gca().invert_yaxis() # flips yaxis
    plt.axis('off')
    
    # plot overlay
    extent = plt.gca().get_xlim() + plt.gca().get_ylim()
    top_down_overlay = plt.imread("../cortical_map_top_down.png")
    plt.imshow(top_down_overlay, interpolation="nearest", extent=extent, zorder=3)
    
    # add colorbar
    #cbar = plt.colorbar(im, shrink=0.3, use_gridspec=True, format="%1.1e")
    #cbar.set_ticks([0, 0.0004, 0.0008, 0.0012])
    #cbar.ax.tick_params(labelsize=6)
    plt.tight_layout()
    
    title = "Map for target pixel ({}, {}) in column {}".format(source_voxel[1], source_voxel[0], source_index)
    #plt.title(title)
    
    #display in tkinter
    figcanvas = FigureCanvasTkAgg(fig, master = canvas)
    figcanvas.get_tk_widget().pack()
    figcanvas.draw()
    
    #canvas.draw()
    plt.close()
    #plt.show()
    #print("Image {} generated".format(img_name))
    #plt.savefig(os.path.join('images/%05d.png' % img_name), bbsource_coordshes=None, facecolor=None, edgecolor=None,transparent=True, dpi=240)
    #filename = str(output_name)+'_factor_'+str(i+1)
    
if __name__ == '__main__':
    #args = parser.parse_args()
    U, V = load_mat.load_solution("top_view_lambda_tv_5.000e+02.mat", "../data/", False)
    plot_svectors(U, V, "top_view", "top_view_lambda_tv_5.000e+02.mat".split('/')[-1], 5000, True)


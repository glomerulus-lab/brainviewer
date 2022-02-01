'''
Script for generating the GIF in the README
See the documentation for more examples and API descriptions:
http://mouse-connectivity-models.readthedocs.io/en/latest/
'''
#TOP-DOWN view

import os
import logging
import subprocess
from os.path import exists


import sys
from PIL.Image import init

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm

from mcmodels.core import Mask, VoxelModelCache
from mcmodels.core.cortical_map import CorticalMap
from matplotlib.widgets import Button


# file path where the data files will be downloaded
MANIFEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '../connectivity', 'mcmodels_manifest.json')
OUTPUT_DIR = 'images'
GIF_CONVERT_COMMAND = 'convert -delay 3x100 -size 50x50 *.png output.gif'
mapper = CorticalMap(projection='top_view')

# check that an argument provided for topview or flatmap version
if len(sys.argv) == 1:
    print('usage: python interactive_flat_map_animate.py  topview | flatmap')
    exit()

top_down_overlay = plt.imread("cortical_map_top_down.png")

def plot_image(x, y): 
    '''
    Plots connectivity for an injection (x,y).
    Parameters:
        x (int)
        y (int)
    '''

    i, val = 0, lookup[x][y]
    print("coords = ", x, y)
    print("val = ", val)    
    filename = str(val) + ".png"
    print(filename)
    img_path = os.path.join(os.getcwd(), 'images', filename);
    file_exists = exists(img_path)
    print(file_exists)
    if file_exists:
        plt.clf()
        img = plt.imread(img_path)
        #plt.gca().set_ylim(114)
        #plt.gca().set_xlim(132)
        #extent = plt.gca().get_xlim() + plt.gca().get_ylim()
        plt.axis('off')
        plt.imshow(img, interpolation="nearest",zorder=3)
        init_buttons()
        plt.draw()




    
def on_press(event):
    '''
    Gets injection coordinates (x,y) and calls function to plot projection.
    Parameters:
        event
    '''
    #scale the x, y coords down to fit the image resolution
    x = int(round(event.xdata) / 10)
    y = int(round(event.ydata) / 10)

    
    if (lookup[x][y] in lookup[lookup > -1]):
        print('you pressed', event.button, x, y)
        plot_image(x, y)
    else:
        print('you pressed', event.button, x, y, 'which is out of bounds.')

    
# initializes buttons
def init_buttons():
    # axis for switch_button
    ax_swtich = plt.axes([0.1, 0.05, 0.1, 0.075])
    # button reference
    switch_button = Button(ax_swtich, 'Switch')

if __name__ == '__main__':
    # caching object for downloading/loading connectivity/model data
    cache = VoxelModelCache(manifest_file=MANIFEST_FILE)

    # 2D Cortical Surface Mapper
    # projection: can change to "flatmap" if desired
    mapper = CorticalMap(projection='top_view')
    if sys.argv[1] == 'flatmap':
        mapper = CorticalMap(projection='dorsal_flatmap')
        
    # quick hack to fix bug
    mapper.view_lookup[51, 69] = mapper.view_lookup[51, 68]
    mapper.view_lookup[51, 44] = mapper.view_lookup[51, 43]

    # colormaps
    cmap_view = matplotlib.cm.inferno
    cmap_pixel = matplotlib.cm.cool
    cmap_view.set_bad(alpha=0)
    cmap_pixel.set_bad(alpha=0)

    # only want R hemisphere
    lookup = mapper.view_lookup.copy().T # transpose for vertical pixel query
    lookup[:lookup.shape[0]//2, :] = -1

    #Begin image plotting and mouse tracking
    fig, ax = plt.subplots(figsize=(6, 7))
    #plt.gca().invert_yaxis()
    plt.axis('off')
    #extent = plt.gca().get_xlim() + plt.gca().get_ylim()
    
    if sys.argv[1] == 'topview':
        img_path = os.path.join(os.getcwd(), 'images', '104.png');
        img = plt.imread(img_path)
        #plt.gca().set_ylim(114)
        #plt.gca().set_xlim(132)
        #extent = plt.gca().get_xlim() + plt.gca().get_ylim()
        plt.imshow(img, interpolation="nearest", zorder=3)
    elif sys.argv[1] == 'flatmap':
        plot_image(200,80)
    cid = fig.canvas.mpl_connect('button_press_event', on_press)

    init_buttons()

    plt.show()
    plt.draw()

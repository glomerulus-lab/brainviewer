'''
Script for generating the GIF in the README
See the documentation for more examples and API descriptions:
http://mouse-connectivity-models.readthedocs.io/en/latest/
'''
#TOP-DOWN view

import os
import logging
import subprocess

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
    
    filename = "images" + i.zfill(5) + ".png"
    print(filename)
    img = plt.imread('images/00000.png')
    plt.imshow(img, interpolation="nearest", zorder=3)

    
def on_press(event):
    '''
    Gets injection coordinates (x,y) and calls function to plot projection.
    Parameters:
        event
    '''
    x = int(round(event.xdata))
    y = int(round(event.ydata))
    print("Coordinates: ", x, y)
  
    if (lookup[x][y] in lookup[lookup > -1]):
        plt.clf()
        print('you pressed', event.button, x, y)
        img = plt.imread('/home/stillwj3/anaconda3/local_mouse/mouse_connectivity_models/examples/movie/images/00001.png')
        plt.axis('off')
        plt.imshow(img, interpolation="nearest",zorder=3)
        init_buttons()
        plt.draw()
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

    print(len(lookup))

    #Begin image plotting and mouse tracking
    fig, ax = plt.subplots(figsize=(6, 6))
    plt.axis('off')
    if sys.argv[1] == 'topview':
        img = plt.imread('images/00000.png')
        plt.imshow(img, interpolation="nearest", zorder=3)
    if sys.argv[1] == 'flatmap':
        plot_image(200,80)
    cid = fig.canvas.mpl_connect('button_press_event', on_press)

    init_buttons()

    plt.show()
    plt.draw()
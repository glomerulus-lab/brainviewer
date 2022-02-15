import os
import logging
import subprocess
from os.path import exists
import time
start = time.perf_counter()

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

mapper = CorticalMap(projection='top_view')
current_overlay = 'init'

# check that an argument provided for topview or flatmap version
if len(sys.argv) != 2:
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
    global switch_button, current_overlay, x_coord, y_coord
    
    i, val = 0, lookup[x][y]

    filename = str(val) + ".png"
    img_path = os.path.join(os.getcwd(), current_overlay + 'Images', filename)

    print("coords = ", x, y)
    print("val = ", val)    
    print("img_name = ", img_path)
    print(exists(img_path))
    
    if exists(img_path):
        plt.clf()
        img = plt.imread(img_path)
        plt.axis('off')
        plt.imshow(img, interpolation="nearest",zorder=3)
        init_buttons()
        plt.draw()
        x_coord = x
        y_coord = y


# Manage key interactions
# Calls to plot_image do not need to be checked
def on_key(event):
    global x_coord, y_coord
    if event.key == 'up':
        plot_image(x_coord, y_coord - 1)
    elif event.key == 'down':
        plot_image(x_coord, y_coord + 1)       
    elif event.key == 'left':
        plot_image(x_coord - 1, y_coord)
    elif event.key == 'right':
        plot_image(x_coord + 1, y_coord)
    else:
        print(event.key + " is an invalid key")
        return
        
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
        start = time.perf_counter()
        plot_image(x, y)
        stop = time.perf_counter()
        print("Plot Time : ", stop - start)
    else:
        print('you pressed', event.button, x, y, 'which is out of bounds.')

def on_switch(event):
    global current_overlay, mapper, lookup, x_coord, y_coord

    # clear the old plot
    plt.clf()
    # handle switching from flatmap to topview
    if current_overlay == 'flatmap':
        current_overlay = 'topview'
        mapper = CorticalMap(projection='top_view')
        # quick hack to fix bug
        mapper.view_lookup[51, 69] = mapper.view_lookup[51, 68]
        mapper.view_lookup[51, 44] = mapper.view_lookup[51, 43]
        # get the new lookup
        lookup = mapper.view_lookup.copy().T # transpose for vertical pixel query
        lookup[:lookup.shape[0]//2, :] = -1
        x_coord = 84
        y_coord = 26
        plot_image(84, 26)

    # handle switching from topview to flatmap
    elif current_overlay == 'topview':
        current_overlay = 'flatmap'
        mapper = CorticalMap(projection='dorsal_flatmap')
        mapper.view_lookup[51, 69] = mapper.view_lookup[51, 68]
        mapper.view_lookup[51, 44] = mapper.view_lookup[51, 43]
        # get the new lookup
        lookup = mapper.view_lookup.copy().T # transpose for vertical pixel query
        lookup[:lookup.shape[0]//2, :] = -1
        x_coord = 200
        y_coord = 80
        plot_image(200,80)
        
# initializes buttons
def init_buttons():
    global switch_button
    # axis for switch_button
    ax_switch = plt.axes([0.1, 0.05, 0.1, 0.075])
    # button reference
    switch_button = Button(ax_switch, 'Switch')
    switch_button.on_clicked(on_switch)
    return switch_button

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
    plt.axis('off')
    
    if sys.argv[1] == 'topview':
        current_overlay = 'topview'
        plot_image(84, 26)
    elif sys.argv[1] == 'flatmap':
        current_overlay = 'flatmap'
        plot_image(200,80)

    fig.canvas.mpl_connect('key_press_event', on_key)
    cid = fig.canvas.mpl_connect('button_press_event', on_press)
    switch_button = init_buttons()
    stop = time.perf_counter()
    print("Startup Time : ", stop-start)
    plt.show()

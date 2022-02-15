'''
Script for generating the GIF in the README
See the documentation for more examples and API descriptions:
http://mouse-connectivity-models.readthedocs.io/en/latest/
'''
#TOP-DOWN view

import os
import logging
from re import X
import subprocess
import time

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
lookup = mapper.view_lookup.copy().T # transpose for vertical pixel query
lookup[:lookup.shape[0]//2, :] = -1

paths = mapper.paths.copy()

current_overlay = "init"

# check that an argument provided for topview or flatmap version
if len(sys.argv) != 2:
    print('usage: python interactive_flat_map_animate.py  topview | flatmap')
    exit()

top_down_overlay = plt.imread("cortical_map_top_down.png")

flat_map_overlay = plt.imread("transparent.png")

x_coord = -1
y_coord = -1

finalPath = [-1,-1,-1]

def top_to_flat(x,y):
    global mapper
    global lookup
    global paths
    ind = np.where(lookup == 30000)

    print("index: ", ind)
    x_flat = 0
    y_flat = 0
    
    for i, val in enumerate(lookup[lookup > -1]):
        path = mapper.paths[val][mapper.paths[val].nonzero()]
        path = np.vstack([np.unravel_index(x, reference_shape) for x in path])
        if (path[0][2] == x and path[0][0] == y):
            ind = np.where(lookup == val)
            x_flat = ind[0][0]
            y_flat = ind[1][0]
            print("xflat: ", x_flat, "| yflat: ", y_flat)
            break

        
    return x_flat, y_flat

def flat_to_top(x,y):
    global mapper
    global lookup
    global paths
    x_top = 0
    y_top = 0

    val = lookup[x][y]
    path = mapper.paths[val][mapper.paths[val].nonzero()]
    path = np.vstack([np.unravel_index(x, reference_shape) for x in path])
    x_top = path[0][2]
    y_top = path[0][0]
        
    return x_top, y_top

    
    
    
# Return -1 when coord is not in lookup
def plot_image(x, y): 
    '''
    Plots connectivity for an injection (x,y).
    Parameters:
        x (int)
        y (int)
    '''
    
    global switch_button
    global current_overlay
    global x_coord, y_coord

    if (lookup[x][y] not in lookup[lookup > -1]):
        print(lookup[x][y])
        return -1
    i, val = 0, lookup[x][y]
    # get the mean path voxel
    print("val = %d" % val)
    print("Evaluating pixel %d" % i)
    path = mapper.paths[val][mapper.paths[val].nonzero()]
    path = np.vstack([np.unravel_index(x, reference_shape) for x in path])
    voxel = tuple(map(int, path.mean(axis=0)))
       
    try:
        row_idx = source_mask.get_flattened_voxel_index(voxel)
    except ValueError:
        print("voxel %s not in mask", voxel)
    else:
        plt.clf()
        # get voxel expression
        volume = target_mask.fill_volume_where_masked(np.zeros(reference_shape),
                                                        voxel_array[row_idx])
        # map to cortical surface
        flat_view = mapper.transform(volume, fill_value=np.nan)

        # injection location
        pixel = np.ma.masked_where(mapper.view_lookup != val, flat_view, copy=False)

        # plot & params
        
        # plot connectivity
        im = plt.pcolormesh(flat_view, zorder=1, cmap=cmap_view, vmin=0, vmax=vmax)
        
        # plot source voxel
        plt.pcolormesh(pixel, zorder=2, cmap=cmap_pixel, vmin=0, vmax=1)
        plt.gca().invert_yaxis() # flips yaxis
        plt.axis('off')
        
        extent = plt.gca().get_xlim() + plt.gca().get_ylim()
        if current_overlay == 'topview':
            # plot top down overlay as appropriate 
            plt.imshow(top_down_overlay, interpolation="nearest", extent=extent, zorder=3)
        else:
            #empty overlay for flatmap
            plt.imshow(flat_map_overlay, interpolation="nearest", extent=extent, zorder=3)
        # add colorbar
        cbar = plt.colorbar(im, shrink=0.3, use_gridspec=True, format="%1.1e")
        cbar.set_ticks([0, 0.0004, 0.0008, 0.0012])
        cbar.ax.tick_params(labelsize=6) 
        plt.tight_layout()
        x_coord = x
        y_coord = y

        # reinitialize buttons
        switch_button = init_buttons()
        plt.draw()
        return 0


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
    
    x = int(round(event.xdata))
    y = int(round(event.ydata))
    if (lookup[x][y] in lookup[lookup > -1]):
        global x_coord, y_coord
        plt.clf()
        print('you pressed', event.button, x, y)
        start = time.perf_counter()
        plot_image(x, y)
        stop = time.perf_counter()
        print("Plot Time: ", stop - start)
        x_coord = x
        y_coord = y
    elif x > 1 or y > 1:
        print('you pressed', event.button, x, y, 'which is out of bounds.')
    

def on_switch(event):

    global current_overlay, mapper, lookup, x_coord, y_coord, paths

    # clear the old plot
    plt.clf()
    # handle switching from flatmap to topview
    if current_overlay == 'flatmap':
        x_top, y_top = flat_to_top(x_coord, y_coord)
        current_overlay = 'topview'
        mapper = CorticalMap(projection='top_view')
        # quick hack to fix bug
        mapper.view_lookup[51, 69] = mapper.view_lookup[51, 68]
        mapper.view_lookup[51, 44] = mapper.view_lookup[51, 43]
        # get the new lookup
        lookup = mapper.view_lookup.copy().T # transpose for vertical pixel query
        lookup[:lookup.shape[0]//2, :] = -1
        paths = mapper.paths.copy()
        plot_image(x_top, y_top)

    # handle switching from topview to flatmap
    elif current_overlay == 'topview':
        
        current_overlay = 'flatmap'
        mapper = CorticalMap(projection='dorsal_flatmap')
        mapper.view_lookup[51, 69] = mapper.view_lookup[51, 68]
        mapper.view_lookup[51, 44] = mapper.view_lookup[51, 43]
        # get the new lookup
        lookup = mapper.view_lookup.copy().T # transpose for vertical pixel query
        lookup[:lookup.shape[0]//2, :] = -1

        paths = mapper.paths.copy()
        x_flat, y_flat = top_to_flat(x_coord, y_coord)
        
        plot_image(x_flat,y_flat)

    
            
def init_buttons():
    global switch_button
    ax_switch = plt.axes([0.1, 0.05, 0.1, 0.075])
    switch_button = Button(ax_switch, 'Switch')
    switch_button.on_clicked(on_switch)
    return switch_button

if __name__ == '__main__':
    start = time.perf_counter()
    # caching object for downloading/loading connectivity/model data
    cache = VoxelModelCache(manifest_file=MANIFEST_FILE)

    # load voxel model
    voxel_array, source_mask, target_mask = cache.get_voxel_connectivity_array()
    reference_shape = source_mask.reference_space.annotation.shape
    vmax = 1.2 * np.percentile(voxel_array.nodes, 99)

    # 2D Cortical Surface Mapper
    # projection: can change to "flatmap" if desired
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
    fig, ax = plt.subplots(figsize=(6, 6))
    if sys.argv[1] == 'topview':
        current_overlay = 'topview'
        print(plot_image(84,26))
    if sys.argv[1] == 'flatmap':
        current_overlay = 'flatmap'        
        print(plot_image(200,80))

    switch_button = init_buttons()
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('key_press_event', on_key)
    print("Startup time : ", time.perf_counter() - start)
    plt.show()



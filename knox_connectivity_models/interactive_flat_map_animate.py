'''
Script for generating the GIF in the README
See the documentation for more examples and API descriptions:
http://mouse-connectivity-models.readthedocs.io/en/latest/
'''
#TOP-DOWN view

import os
import logging
import subprocess

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm

from mcmodels.core import Mask, VoxelModelCache
from mcmodels.core.cortical_map import CorticalMap


# file path where the data files will be downloaded
MANIFEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '../connectivity', 'mcmodels_manifest.json')
OUTPUT_DIR = 'images'
GIF_CONVERT_COMMAND = 'convert -delay 3x100 -size 50x50 *.png output.gif'

top_down_overlay = plt.imread("cortical_map_top_down.png")

def main():
    # caching object for downloading/loading connectivity/model data
    cache = VoxelModelCache(manifest_file=MANIFEST_FILE)

    # load voxel model
    voxel_array, source_mask, target_mask = cache.get_voxel_connectivity_array()

    reference_shape = source_mask.reference_space.annotation.shape
    vmax = 1.2 * np.percentile(voxel_array.nodes, 99)

    # 2D Cortical Surface Mapper
    # projection: can change to "flatmap" if desired
    mapper = CorticalMap(projection='top_view')
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
    return lookup, mapper, voxel_array, source_mask, target_mask, reference_shape, cmap_view, vmax


def plot_image(x, y): 
    '''
    Plots connectivity for an injection (x,y).
    Parameters:
        x (int)
        y (int)
    '''
    
    i, val = 0, lookup[x][y]
    # get the mean path voxel
    print("Evaluating pixel %d" % i)
    path = mapper.paths[val][mapper.paths[val].nonzero()]
    path = np.vstack([np.unravel_index(x, reference_shape) for x in path])
    voxel = tuple(map(int, path.mean(axis=0)))

    try:
        row_idx = source_mask.get_flattened_voxel_index(voxel)
    except ValueError:
        print("voxel %s not in mask", voxel)
    else:
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
        
        # plot overlay
        extent = plt.gca().get_xlim() + plt.gca().get_ylim()
        plt.imshow(top_down_overlay, interpolation="nearest", extent=extent, zorder=3)
        
        # add colorbar
        cbar = plt.colorbar(im, shrink=0.3, use_gridspec=True, format="%1.1e")
        cbar.set_ticks([0, 0.0004, 0.0008, 0.0012])
        cbar.ax.tick_params(labelsize=6) 
        plt.tight_layout()

def on_press(event):
    x = int(round(event.xdata))
    y = int(round(event.ydata))
    if (lookup[x][y] in lookup[lookup > -1]):
        plt.clf()
        print('you pressed', event.button, x, y)
        plot_image(x, y)
        plt.draw()
    else:
        print('you pressed', event.button, x, y, 'which is out of bounds.')
    
if __name__ == '__main__':
    # caching object for downloading/loading connectivity/model data
    cache = VoxelModelCache(manifest_file=MANIFEST_FILE)

    # load voxel model
    voxel_array, source_mask, target_mask = cache.get_voxel_connectivity_array()
    reference_shape = source_mask.reference_space.annotation.shape
    vmax = 1.2 * np.percentile(voxel_array.nodes, 99)

    # 2D Cortical Surface Mapper
    # projection: can change to "flatmap" if desired
    mapper = CorticalMap(projection='top_view')
    
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
    plot_image(-1,-1)
    cid = fig.canvas.mpl_connect('button_press_event', on_press)
    plt.show()
    plt.draw()

from tkinter import *

import os
import logging
import subprocess

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm

from mcmodels.core import Mask, VoxelModelCache
from mcmodels.core.cortical_map import CorticalMap

logger = logging.getLogger(name=__name__)

# file path where the data files will be downloaded
MANIFEST_FILE = os.path.join(os.path.dirname(os.path.abspath('')),
                             '../connectivity', 'mcmodels_manifest.json')
OUTPUT_DIR = 'images'
GIF_CONVERT_COMMAND = 'convert -delay 3x100 -size 50x50 *.png output.gif'

top_down_overlay = plt.imread("cortical_map_top_down.png")


# window dimensions (132,114)x2
window_width = 264
window_height = 228

window = Tk()
window.title('Brainviewer')

window_geo = (str(window_height) + 'x' + str(window_width) + '+10+20')
window.geometry(window_geo)
window.minsize(window_width, window_height)
window.maxsize(window_width, window_height)

greeting = Label(text="Welcome to BrainviewerUI!")
greeting.pack()

#on mouse motion within the window, changes the title to reflect coords of mouse pos.
def get_plot_at_position(x, y):
    
    # put plotting stuff here then move this file to proper directory
    # use x,y to return plot. Fill this def with plotting 

def get_cursor_position(event):
    x = event.x
    y = event.y
    
    # limit cursor update to bounds of the window
    if x >= 0 and y >= 0:
        if x <= window_width and y <= window_height:
            plt = get_plot_at_position(x,y)
            # use tkinter to put plot in window
            cursor_coords = '{}, {}'.format(event.x, event.y)
            window.title(cursor_coords)

def main():

    #on mouse motion within the window, change title to reflect cursor position
    window.bind('<Motion>', get_cursor_position)
    window.mainloop()



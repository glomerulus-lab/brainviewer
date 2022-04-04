import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm

OUTPUT_DIR = "data/colorbar.png"

vmax = 0.0013824748294428008
cmap_view = matplotlib.cm.inferno

cbar_axes = plt.axes([0.9, 0.3, 0.025, 0.5])
cbar_ticks = [0, 0.0004, 0.0008, 0.0012]
norm = matplotlib.colors.Normalize(vmin = 0, vmax = vmax)
cbar = matplotlib.colorbar.ColorbarBase(ax = cbar_axes, cmap = cmap_view, ticks = cbar_ticks, norm = norm)
cbar.ax.tick_params(labelsize=6)
plt.savefig(OUTPUT_DIR, bbox_inches='tight')

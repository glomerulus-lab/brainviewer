import numpy as np
import matplotlib.pyplot as plt 
import matplotlib as mpl
import math 



def plot(x, y, xlabel, ylabel, title, bounds, c_title, start, end):
    '''Returns plot with basic line curve and log colorbar
    
    Parameters:
        x (list): x-axis values
        y (list): y-axis values
        xlabel (str): x-axis label
        ylabel (str): y-axis label
        title (str): figure title
        bounds (list): numbers to mapped to color
        c_title (str): colorbar title
        start (int or float): first colorbar value
        end (int or float): last colorbar value
    '''

    plt.rc('xtick',labelsize=11)
    plt.rc('ytick',labelsize=11)

    # Plot data
    plt.plot(x, y, linestyle="-", color='k', zorder=2)
    # plt.loglog(x, y, linestyle="-", color='k', zorder=2)
    plt.scatter(x,y, 50, bounds, zorder=3)

    # Add colorbar and labels
    cmap = mpl.cm.viridis
    norm = mpl.colors.LogNorm(start, end, cmap.N)
    cb = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap))
    cb.set_label(label=c_title, size=16, rotation=360)
 
    axis_font = {'size':'16'}
    title_font = {'size':'18'}
    plt.xlabel(xlabel, **axis_font)
    plt.ylabel(ylabel, **axis_font)
    plt.title(title, **title_font)

    return plt

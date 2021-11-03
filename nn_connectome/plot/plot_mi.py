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

if __name__ == '__main__':
    U, V = load_mat.load_solution(solution_name, '../../lowrank_connectome/matlab/solution/',greedy)

import numpy as np
import scipy.io as sci
import matplotlib.pyplot as plt 
import matplotlib as mpl
import argparse
import glob
import math 
import copy 
import matplotlib.pyplot as plt
import matplotlib as mpl
from plot_curve import plot as pltter
import sys, inspect, os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from util.sort import sort_vals
from util.sort import sort_vals2
 

 

parser = argparse.ArgumentParser(description='Plot dominant factors of connectome solution')
# Arguments
parser.add_argument('testname',              type=str, nargs=1, help='Name of test to plot: "test", "top_view" or "flatmap".')
parser.add_argument('path_to_solution',      type=str, nargs=1, help='Path to .mat solution file, excluding filename.')
parser.add_argument('solution_name',         type=str, nargs=1, help='Name of .mat solution file, including or excluding file extension.')
parser.add_argument('title',                 type=str, nargs=1, help='Title of relative RMSE curve.')
# Flags
parser.add_argument('-nneg', action='store_true', help='Determines key used to get lambda value. When nonnegative solution used: nneg=True.')



def save_location(testname):
    if(testname == 'test'):
        path = "../data/lambda_tests/"
    elif(testname == 'top_view'):
        path = "../data/lambda_tv/"
    elif(testname == 'flatmap'):
        path = "../data/lambda_fm/"
    return path


def plot_relative_RMSE(testname, path, output, title, greedy=True):
    '''Returns figure comparing relative RMSE and lambda. 
    Also, for top_view and flatmap problems, the horizontal line at y=0.2 estimates reasonable error.'''
    if(greedy):
        data = sci.loadmat(path+testname+'.mat')
    else:   
        data = sci.loadmat(path+'nneg_test.mat')

    keys = list(data.keys())[3:]

    # Get relative MSE
    rmse = []
    lambdas = []
    for key in keys:
        lambdas.append(float(data[key][0][0]))
        rmse.append(data[key][0][1])
    
    # Sort keys 
    keys, rmse = sort_vals2(lambdas, rmse)
    logkey = copy.deepcopy(keys)
    for x in range(len(keys)):
        logkey[x] = math.log10(logkey[x])

    plt = pltter(keys, rmse, r'$\lambda$', "Relative RMSE", title, logkey, r'$\lambda$', keys[0], keys[len(keys)-1])
    if(testname != 'test'):
        plt.axhline(y=0.2, color='grey', linestyle='--')

    # Mark the optimal lambda values with an X
    px=0
    py=0
    for i in range(len(logkey)):
        if(testname == 'flatmap' and logkey[i]==7):
            px = keys[i]
            py = rmse[i]
        elif(logkey[i]==4 and not testname == 'flatmap'):
            px = keys[i]
            py = rmse[i]

    plt.plot(px,py, 'x', color='tomato', zorder=100,mew=4, markersize=12)
    plt.xscale('log')
    plt.tight_layout()
    path = save_location(testname)
    plt.savefig(path+output+".png")



if __name__ == '__main__':
    args = parser.parse_args()
    print('solution_name: ', args.solution_name[0], '\npath_to_solution: ', args.path_to_solution[0], '\ntitle: ', args.title[0])
    if(args.nneg):
        print('begin nonnegative relative RMSE plot')
        plot_relative_RMSE(args.testname[0], args.path_to_solution[0], args.solution_name[0], args.title[0], False)

    else:
        print('begin greedy relative RMSE plot')
        plot_relative_RMSE(args.testname[0], args.path_to_solution[0], args.solution_name[0], args.title[0])
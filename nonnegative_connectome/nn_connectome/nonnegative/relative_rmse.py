import numpy as np
import scipy.linalg
import sys, inspect, os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import optimization.alt_acc_prox_grad as alt_acc_prox_grad
import util.math_util as math_util
import util.load_mat as load_mat
import time
import glob
import math
import scipy.io as sci

counts = [0,0,0]
times = [0,0,0]
test_size = 356089.92794818647
tv_size = 63616.72461631253
fm_size = 161654.23869936168


parser = argparse.ArgumentParser(description='Plot dominant factors of connectome solution')
# Arguments
parser.add_argument('testname',              type=str, nargs=1, help='Name of test to plot. "test", "top_view" or "flatmap".')
parser.add_argument('solution_name',         type=str, nargs=1, help='Name of .mat solution file, including or excluding file extension.')
parser.add_argument('path_to_solution',      type=str, nargs=1, help='Path to .mat solution file, excluding filename.')
# Flags
parser.add_argument('-nneg', action='store_true', help='Determines key used to get lambda value. When nonnegative solution used: nneg=True.')
  


def P_Omega(X, Omega):
    # print("P_omega")
    X[Omega.toarray()==1] = 0
    return X

# 2 different ways to calculate the regularization. Value used is hardcoded in at top.
# def regularized_cost(U, V, X, Y, Lx, Ly, lamb, Omega):
#     counts[0] += 1
#     start_time = time.time()
    
#     result = np.linalg.norm(P_Omega(U @ (V.T @ X) - Y, Omega), ord='fro')**2
#     result = result + lamb * math_util.factorized_sum_frobenius_sq_j_einsum(Ly @ U, V.T, U, V.T @ Lx.T)
#     times[0] += time.time() - start_time

#     return result

# def regularization(U, V, Lx, Ly, lamb):
#     regularization = math_util.factorized_sum_frobenius_sq_j_einsum(Ly @ U, V.T, U, V.T @ Lx.T)
#     return regularization


def loss(U, V, X, Y, Omega):
    loss = np.linalg.norm(P_Omega(U @ (V.T @ X) - Y, Omega), ord='fro')**2
    return loss

# 1st approach to calculating relative RMSE
def size(Y, Omega):
    size = np.linalg.norm(P_Omega(Y, Omega), ord='fro')**2
    return size

# Second approach to calculating relative RMSE
def size2(U, V, X, Y, Omega):
    y_pred = U @ (V.T @ X)
    size = (np.linalg.norm(P_Omega(y_pred, Omega), ord='fro')**2) + (np.linalg.norm(P_Omega(Y, Omega), ord='fro')**2)/2
    return size


def pick_size(testname):
    if(testname == 'test'):
        return test_size
    elif(testname == 'top_view'):
        return tv_size
    elif(testname == 'flatmap'):
        return fm_size


def relative_RMSE(path,files,testname,nneg=False):
    save={}
    # Iterate over files and save data
    for filepath in glob.glob(path+files):
        head, tail = os.path.split(filepath)
        U,V = load_mat.load_solution(tail, path, True)
        os.chdir("..")
        matrices = load_mat.load_all_matricies(testname)
        os.chdir("nonnegative")
        values = sci.loadmat(filepath)

        # Calculate relative_MSE using python data
        sz = pick_size(testname)
        loss_val = loss(U, V.T, matrices['X'], matrices['Y'], matrices['Omega'])
        relative_RMSE = loss_val/sz 
        save[tail] = [values["lambda"][0][0], math.sqrt(relative_RMSE)]

    # Save data        
    if(nneg):
        scipy.io.savemat("relative_mse/nneg_"+testname+".mat", save)
    else:
        scipy.io.savemat("relative_mse/"+testname+".mat", save)


# Used for relative RMSE figures in appendix
def relative_RMSE2(path,files,testname,nneg=False):
    save={}
    # Iterate over files and save data
    for filepath in glob.glob(path+files):
        head, tail = os.path.split(filepath)
        U,V = load_mat.load_solution(tail, path, True)
        os.chdir("..")
        matrices = load_mat.load_all_matricies(testname)
        os.chdir("nonnegative")
        values = sci.loadmat(filepath)

        # Calculate relative_MSE using python data
        sz = size2(U, V.T, matrices['X'], matrices['Y'], matrices['Omega'])
        loss_val = loss(U, V.T, matrices['X'], matrices['Y'], matrices['Omega'])
        relative_RMSE = loss_val/sz 
        save[tail] = [values["hp_lamb"][0][0], math.sqrt(relative_RMSE)]

    # Save data        
    if(nneg):
        scipy.io.savemat("relative_mse2/nneg_"+testname+".mat", save)
    else:
        scipy.io.savemat("relative_mse2/"+testname+".mat", save)


if __name__ == '__main__':
    '''Calculate the relative RMSE for a number of solutions. This data can be used by plit_rmse.py.'''
    args = parser.parse_args()
    relative_RMSE2(args.path_to_solution[0], args.solution_name[0], args.testname[0], args.nneg)
    relative_RMSE(args.path_to_solution[0], args.solution_name[0], args.testname[0], args.nneg)
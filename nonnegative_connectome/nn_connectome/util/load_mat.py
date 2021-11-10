import numpy as np
import scipy.io


def load_lamb(name, folder, greedy=False,):
    ''' 
    Returns the lambda value from a given '.mat' file for a connectome solution.
    
    Parameters:
        name (str): file name of solution
        folder (str): path to where solution is located
    Optional Parameters:
        greedy (boolean): False indicates the solution is nonnegative (default), True indicates the solution is unconstrained
    '''

    filename =''
    try:
        filename = folder+name
        print(filename)
        data = scipy.io.loadmat(filename, variable_names ='lamb')
        lamb = data['lamb'][0][0]
        return lamb

    except:
        # Solution file not found
        if(greedy):
            print("Solution from '" + filename + "' could not be found, make sure a solution exists by running test_allvis_completion.m. Exitting.")
        else:
            print("Solution from '" + filename + "' could not be found, Exitting.")
        exit(1)


def load_solution(name, folder, greedy=False):
    '''
    Returns U and V.T from a given '.mat' file for a connectome solution. Shapes are as follows:
        full (low rank) solution X = U @ V
        U is nx * r
        V is r * ny
    Parameters:
        name (str): file name of solution
        folder (str): path to where solution is located
    Optional Parameters:
        greedy (boolean): False indicates the solution is nonnegative (default), True indicates the solution is unconstrained
    '''

    try:
        filename = folder+ name
        data = scipy.io.loadmat(filename, variable_names="W")
        return data["W"][0][0], np.transpose(data["W"][1][0])

    except:
        # Solution file not found
        if(greedy):
            print("Solution from '" + filename + "' could not be found, make sure a solution exists by running test_allvis_completion.m. Exitting.")
        else:
            print("Solution from '" + filename + "' could not be found, Exitting.")
        exit(1)
    


# 
def load_test_truth():
    '''Returns W_true with shape (200, 200) from the true test solution.'''
    try:
        data = scipy.io.loadmat("../../lowrank_connectome/data/test_matrices.mat")
        return data["W_true"]

    except:
        print("W_true from '../../lowrank_connectome/data/test_matrices.mat' could not be found, Exitting.")
        exit(1)


def load_voxel_coords(testname):
    '''Returns source and target voxel coordinates and the lookup table (lut) for top-view and flatmap solutions.'''
    try:
        data = scipy.io.loadmat("../../lowrank_connectome/data/"+testname+"_matrices.mat")
        voxel_coords_source = data["voxel_coords_source"]
        voxel_coords_target = data["voxel_coords_target"]
        view_lut = data["view_lut"]
        return  voxel_coords_source, voxel_coords_target, view_lut

    except:
        print("'Voxel coordinates from '../../lowrank_connectome/data/"+testname+"_matrices.mat' could not be found, Exitting.")
        exit(1)

    return voxel_coords_source, voxel_coords_target, view_lut


def load_tvoxel_coords(testname):
    '''Returns source and target voxel coordinates for test solutions.'''
    try:
        data = scipy.io.loadmat("../../lowrank_connectome/data/"+testname+"_matrices.mat")
        voxel_coords_source = data["voxel_coords_source"]
        voxel_coords_target = data["voxel_coords_target"]
    except:
        print("'Voxel coordinates from '../../lowrank_connectome/data/"+testname+"_matrices.mat' could not be found, Exitting.")
        exit(1)
    return voxel_coords_source, voxel_coords_target


def load_all_matricies(testname):
    '''Returns all data for test, top-view, or flatmap solutions in the directory lowrank_connectome/data/ .'''
    try:
        data = scipy.io.loadmat("../lowrank_connectome/data/"+testname+"_matrices.mat")
        data["Omega"] = data["Omega"].astype(np.int8)
        data["Lx"] = data["Lx"].astype(np.int8)
        data["Ly"] = data["Ly"].astype(np.int8)
        return data

    except:
        print("'Matricies data from '../lowrank_connectome/data/"+testname+"_matrices.mat' could not be found, Exitting.")
        exit(1)

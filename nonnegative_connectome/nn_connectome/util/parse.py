import scipy.io as sci
import glob
import collections 
import copy 


def parse(filename, greedy=True):
    '''
    Returns a lists for loss, regularization, cost and lambda values for a series of files
    Parameters:
        filename (str): full path to solution + name of file(s) to parse 
    Optional Parameters
        greedy (boolean): False indicates solution is unconstrained (default)
    '''

    # parse data for each file
    regs = []
    losses=[]
    costs = []
    lambs = []
    # Does not need entire filename ex. '/some/dir/filena*' will return all files in dir beginning with 'filena'
    for filepath in glob.glob(filename):
        if(greedy):
            list_variables= ["cost","loss","reg","lamb"]
        else:
            list_variables= ["cost_final", "loss_final", "reg_final", "hp_lamb"]
        
        data = sci.loadmat(filepath, variable_names=list_variables[0])
        costs.append(data[list_variables[0]][0][0])
        data = sci.loadmat(filepath, variable_names=list_variables[1])
        losses.append(data[list_variables[1]][0][0])
        data = sci.loadmat(filepath, variable_names=list_variables[2])
        regs.append(data[list_variables[2]][0][0])
        data = sci.loadmat(filepath, variable_names=list_variables[3])
        lambs.append(data[list_variables[3]][0][0])

    return losses,regs,costs,lambs

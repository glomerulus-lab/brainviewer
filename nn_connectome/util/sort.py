import numpy as np
import collections 
import math 


def sort_vals(key, vals):
    '''
    Returns sorted lists in ascending order with entries that remain paired by index, where key = log10(key).

    Parameters:
        key (list): list of values to be sorted on (act as dictionary key)
        vals (list): list of values to be sorted according to their corresponding key
    '''

    dict_sort = {}
    # Create a dictionary, where key = keys and vals = corresponding key's value
    for x in range(len(key)):
        key[x] = math.log10(key[x])
        dict_sort[key[x]]= [vals[x]] 
    # Sort dict by order of keys
    dict_sort = collections.OrderedDict(sorted(dict_sort.items()))
    key.sort()

    # Update vals to match sorted order
    for x in range(len(key)):
        vals[x] = dict_sort[key[x]][0]
    return key, vals
    

def sort_vals2(key, vals):
    '''
    Returns sorted lists in ascending order with entries that remain paired by index.

    Parameters:
        key (list): list of values to be sorted on (act as dictionary key)
        vals (list): list of values to be sorted according to their corresponding key
    '''
    
    dict_sort = {}
    # Create a dictionary, where key = keys and vals = corresponding key's value
    for x in range(len(key)):
        key[x] = key[x]
        dict_sort[key[x]]= [vals[x]] 
    # Sort dict by order of keys
    dict_sort = collections.OrderedDict(sorted(dict_sort.items()))
    key.sort()

    # Update vals to match sorted order
    for x in range(len(key)):
        vals[x] = dict_sort[key[x]][0]
    return key, vals
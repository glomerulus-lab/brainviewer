import argparse
import matplotlib.pyplot as plt
import seaborn as sns # for heatmap generation
import os
import sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
import util.load_mat as load_mat

parser = argparse.ArgumentParser(description="Creates a heatmap of solution.")
parser.add_argument('solution_name',  type=str, nargs=1,
                   help='Name of solution to plot')
parser.add_argument('output_file',  type=str, nargs=1,
                   help='name of file to save to')


def create_heatmap(U, V, output_file):
    '''Create a heatmap for specified solution using U & V.'''     
    # Ask user to confirm plots for large solutions
    if(U.shape[0] > 1000 or V.shape[1] > 1000):
        cont = input("Warning: Xolution is large, ("+str(U.shape[0])+", "+str(V.shape[1])+"). Continue? (y/n)")
        if (cont.lower() != "y"):
            print("Exitting plot_solution.py")
            exit()

    # Compute solution        
    X = U @ V
    rank = U.shape[1]

    # Plot solution
    ax = sns.heatmap( X, cmap="Reds", cbar=True, xticklabels=[], yticklabels=[])
    ax.tick_params(left=False, bottom=False) ## other options are right and top

    plt.title("$\mathregular{W_{"+str(rank)+"}}$")
    # Save plot as file
    plt.savefig(output_file, bbox_inches='tight')
    plt.clf()



def create_heatmap_test_truth(output_file):
    '''Returns heatmap of the true test solution.'''
    W = load_mat.load_test_truth()
    # Plot solution
    title_font = {'size':'18', 'weight':'bold'}
    ax = sns.heatmap( W, cmap="Reds", cbar=True, xticklabels=[], yticklabels=[])
    plt.title("$\mathregular{W_{Truth}}$", title_font)

    # Save plot as file
    plt.savefig(output_file, bbox_inches='tight')
    plt.clf()
    
    
def create_heatmap_from_solution(solution_name, output_file, greedy=False):
    '''Wrapper for create_heatmap that accepts a solution file to load and provides U and V.'''
    U, V = load_mat.load_solution(solution_name, '../../lowrank_connectome/matlab/solution/',greedy)
    create_heatmap(U, V, output_file)


if __name__ == '__main__':
    args = parser.parse_args()
    create_heatmap_from_solution(args.solution_name[0], args.output_file[0])
    # create_heatmap_test_truth(args.output_file[0])
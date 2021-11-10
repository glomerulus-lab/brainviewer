import matplotlib.pyplot as plt
import scipy.io
import numpy as np
import argparse



parser = argparse.ArgumentParser(description='Plot dominant factors of connectome solution')
# Arguments
parser.add_argument('suffixes',    type=str, nargs=1, help='How many tests were done (each test contains steps 0-160)')
parser.add_argument('directory_path', type=str, nargs=1, help='Directory path where solutions are located')



def calc_refinement_time(dir, suffixes, steps):
    '''
    Returns the average time spent completing for each step (number of refinements) for the inital and final refinement stages.
    
    Parameters:
        dir (str) : Entire directory path where solutions are located
        suffixes (arr of str) : A list of strings for representing each test of x steps
        steps : The range iterations used for each test (each solution uses some number of iterations within this range)
    '''
    refining = []
    final = []
    # Load time data from each solution
    for step in steps:
        avg_ref = 0
        avg_fin = 0
        for suffix in suffixes:
            data = scipy.io.loadmat(dir + suffix +str(step))
            avg_ref += data["time_refining"][0][0]
            avg_fin += data["time_final_solution"][0][0]

        # Calculate the refinement steps' and final steps' average run times
        refining.append(avg_ref/len(suffixes))
        final.append(avg_fin/len(suffixes))
    return refining, final


def plot_init_quality(refining, final, steps):
    ''' Returns a graph of time vs refinement iterations.'''
    # Plot the final regression and initial refinement for each solution
    plt.figure()
    plt.clf()
    plt.bar(steps, final, width=8, label="Final regression", bottom = refining, color="#1f77b4")
    plt.bar(steps, refining, width=8, label="Initialization refinement",color="#ff7f0e")
    # Add titles, labels, legend
    axis_font = {'size':'13'}
    legend_font = {'size':'11'}
    title_font = {'size':'15'}
    plt.xlabel("Refinement iterations", **axis_font)
    plt.ylabel("Time (s)", **axis_font)
    plt.title("Time to Convergence", **title_font)
    plt.legend(loc="best", prop=legend_font)
    plt.savefig("init_quality")
    plt.close()


if __name__ == '__main__':
    '''
    Returns a bar graph displaying the impact of the number of refinement iterations on the average runtime of nonnegative_converter.py.
    
    Note: See tv_quality.py for an example of the data used for this figure.
    '''
    args = parser.parse_args()
    dir = args.directory_path[0]
    suffixes=[]
    for x in range(int(args.suffixes[0])):
        suffixes.append("test_test_init_quality_"+str(x)+"_")
    steps = np.arange(0,160,10)
    refining, final = calc_refinement_time(dir, suffixes, steps)
    plot_init_quality(refining,final, steps)
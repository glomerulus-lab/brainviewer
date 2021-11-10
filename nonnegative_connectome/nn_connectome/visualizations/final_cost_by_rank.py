import matplotlib.pyplot as plt
import scipy.io
import numpy as np
import math
import argparse

parser = argparse.ArgumentParser(description='Plot dominant factors of connectome solution')
# Arguments
parser.add_argument('testname',    type=str, nargs=1, help='test, top_view, or flatmap')
parser.add_argument('directory_path', type=str, nargs=1, help='Directory path to where solutions are located')

# Retrieve final costs data for nonnegative and unconstrained solutions
def load_final_cost_data(tests,tests_dir):
    greedy_cost = []
    nneg_cost = []
    ranks = []
    for test in tests:
        test_data = scipy.io.loadmat(tests_dir + test)

        # Get costs
        greedy_cost.append(test_data["cost_greedy"][0][0])
        nneg_cost.append(test_data["cost_final"][0][0])
        
        # Get and report time to complete each solution
        time = test_data["time_problem_setup"][0][0] + test_data["time_load_greedy"][0][0] 
        time = time + test_data["time_initialization"][0][0] + test_data["time_refining"][0][0]
        time = time + test_data["time_final_solution"][0][0]
        ranks.append(test_data["W"][0][0].shape[1])
        print(str(test_data["W"][0][0].shape[1]) + " time: " + str(time/60))

    greedy_ranks = []
    for rank in ranks:
        greedy_ranks.append(int((rank+1)/2))

    return ranks, greedy_ranks, nneg_cost, greedy_cost, time

def plot_final_cost(ranks, greedy_ranks, nneg_cost, greedy_cost):
    '''Plot the final costs of nonnegative and unconstrained solutions.'''
    plt.figure()
    plt.clf()

    # Add dotted line to connect related unconstrained and nonnegative solutions
    for i in range(len(ranks)):
        plt.plot([ranks[i],greedy_ranks[i]], [nneg_cost[i], greedy_cost[i]], color="grey", linestyle="--")
        
    plt.rc('xtick',labelsize=13)
    plt.rc('ytick',labelsize=13)

    # Plot nonnegative and unconstrained costs
    plt.plot(ranks, nneg_cost, label="Nonnegative", color="navy", linestyle="-", marker=".", markersize="10")
    plt.plot(greedy_ranks, greedy_cost, label="Unconstrained", color="tomato", linestyle="-", marker=".", markersize="10")
    
    # Set labels, titles, font sizes
    plt.plot([], [], color="grey", linestyle="--", label="Related solutions")
    axis_font = {'size':'16'}
    legend_font = {'size':'14'}
    title_font = {'size':'18'}
    plt.xlabel("Solution rank", **axis_font), plt.xticks(ticks=range(0,1100,100))
    plt.ylabel("Final cost", **axis_font)
    plt.legend(loc="best",prop=legend_font)
    
    # Save figure
    if(testname=="top_view"):
        plt.title("Final Cost by Rank of Top-View Solution",**title_font)
        plt.savefig("final_tv_cost_by_rank", bbox_inches="tight")
    elif(testname == "flatmap"):
        plt.title("Final Cost by Rank of Flatmap Solution",**title_font)
        plt.savefig("final_fm_cost_by_rank", bbox_inches="tight")
    plt.close()

def avg_diff_in_costs(nneg_cost,greedy_cost):
    ''' Returns the average difference in costs between nonnegative and greedy solutions for high ranking solutions. '''
    totaldiff = 0
    for x in range(len(nneg_cost)):
        nneg = nneg_cost[x]
        greedy = greedy_cost[x]
        diff = (nneg-greedy) / ((nneg+greedy)/2)
        diff = diff * 100

        if(ranks[x]>99):
            # Take absolute value
            totaldiff += math.fabs(diff)
    # Only for ranks = {100, 250, 500}
    avg = totaldiff/3
    print("The average difference between high ranking unconstrained (100-500) and nonnegative (199-999) solutions: "+str(avg))



if __name__ == '__main__':
    args = parser.parse_args()
    tests_dir = args.directory_path[0]
    testname = args.testname[0]

    # Will store filenames of various ranking solutions
    tests=[]

    # Flatmap or top-view intial solution ranks = {20, 50, 100, 250, 500}
    if(testname == "top_view"):
        tests = [
            "top_view_lambda_tv_2.000e+01.mat",
            "top_view_lambda_tv_5.000e+01.mat",
            "top_view_lambda_tv_1.000e+02.mat",
            "top_view_lambda_tv_1.000e+04.mat",
            "top_view_lambda_tv_5.000e+02.mat",
        ]
    elif(testname == "flatmap"):
        tests = [
            "flatmap_lambda_2.000e+01.mat",
            "flatmap_lambda_5.000e+01.mat",
            "flatmap_lambda_1.000e+02.mat",
            "flatmap_lambda_2.500e+02.mat",
            "flatmap_lambda_5.000e+02.mat",
        ]
    
    # Get final costs
    ranks, greedy_ranks, nneg_cost, greedy_cost, time = load_final_cost_data(tests, tests_dir)
    # Plot final costs by rank
    plot_final_cost(ranks, greedy_ranks, nneg_cost, greedy_cost)
    # Calculate average difference in costs
    avg_diff_in_costs(greedy_cost, nneg_cost)
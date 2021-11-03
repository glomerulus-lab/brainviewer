import matplotlib.pyplot as plt
import scipy.io
import numpy as np



tests_dir = "/home/mcculls5/Documents/glomerulus/nonnegative_connectome/data/"
tests = [
    "nonnegative_top_view_top_view_20_e4e5.mat",
    "nonnegative_top_view_top_view_50_e4e5.mat",
    "nonnegative_top_view_top_view_100_e4e5.mat",
    "nonnegative_top_view_top_view_250_full.mat",
    "nonnegative_top_view_top_view_500_e4e5.mat",
]

test_names = [
    "Rank 20",
    "Rank 50",
    "Rank 100",
    "Rank 250",
    "Rank 500",
]

ranks=[]

data = []

for test in tests:
    test_data = scipy.io.loadmat(tests_dir + test)

    time = test_data["time_refining"][0][0]
    time += test_data["time_final_solution"][0][0]
    ranks.append(test_data["W"][0][0].shape[1])
    data.append(time)

#

plt.figure()
plt.clf()


plt.plot(ranks, data, color="navy", linestyle="-", marker=".", markersize="10")

for i in range(len(ranks)):
    print(ranks[i], data[i])

# plt.yscale("log")
plt.xlabel("Solution Rank")
plt.xticks(ticks=range(0,1100,100))
plt.ylabel("Total Runtime (Seconds)")
plt.title("Total Runtime by Solution Rank")
# plt.legend(loc="best")
plt.savefig("time_by_rank",  bbox_inches="tight")
plt.close()
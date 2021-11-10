import matplotlib.pyplot as plt
import scipy.io
import numpy as np

#These functions accomplish the same thing
# def get_rank_1_magnitudes(U, V):
#     rank = U.shape[1]
#     magnitudes = []
#     for i in range(rank):
#         U_r = U[:,i:i+1]
#         V_r = V[i:i+1,:]
#         magnitudes.append(np.sqrt(np.trace(np.linalg.multi_dot([U_r.T, U_r, V_r, V_r.T]))))
        
#     return np.sort(magnitudes)[::-1] # sort descending

def get_factor_magnitudes(U, V):
    rank = U.shape[1]
    magnitudes = []
    for i in range(rank):
        U_r = U[:,i:i+1]
        V_r = V[i:i+1,:]

        magnitudes.append(np.linalg.norm(U_r) * np.linalg.norm(V_r))

    return np.sort(magnitudes)[::-1] # sort descending


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

colors = [
    "b",
    "g",
    "r",
    "c",
    "k"
]

data = []
for test in tests:
    test_data = scipy.io.loadmat(tests_dir + test)
    U = test_data["W"][0][0]
    V = test_data["W"][1][0].T

    data.append(get_factor_magnitudes(U, V))




plt.figure()
plt.clf()
for i in range(len(data)):
    plt.plot(range(len(data[i])), data[i], colors[i]+"-", label=test_names[i])
plt.yscale("log")
plt.xlabel("Rank 1 factors")
plt.ylabel("Frobenius Norm")
plt.title("Factor Magnitude Distribution")
plt.legend(loc="best")
plt.savefig("factor_magnitude_distribution")
plt.close()
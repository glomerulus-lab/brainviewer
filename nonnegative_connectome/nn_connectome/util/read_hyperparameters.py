import scipy.io
experiments = ["../data/nonnegative_top_view_top_view_100_tol_e-4_e-5", "../data/nonnegative_flatmap_flatmap_100_tol_e-4_e-5", "data/nonnegative_top_view_top_view_100_tol_e-5", "data/nonnegative_flatmap_flatmap_100_tol_e-5"]

for experiment in experiments:
    data = scipy.io.loadmat(experiment)

    print(data["time_refining"], data["time_final_solution"], data["cost_final"])
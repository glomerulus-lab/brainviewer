import numpy as np
import scipy.linalg
import sys, inspect, os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import optimization.alt_acc_prox_grad as alt_acc_prox_grad
import util.math_util as math_util
import time

counts = [0,0,0]
times = [0,0,0]

def optimize_alt_pgd(U, V,
                    X, Y, Lx, Ly, Omega,
                    lamb,
                    tol=1e-10,
                    alt_tol=1e-5,
                    max_outer_iter=10,
                    max_inner_iter=10,
                    max_line_iter=100,
                    calculate_cost=True):

    U = np.array(U)
    V = np.array(V)
    print("Performing PDG on regularized nonnegative regression problem.")
    U, V, costs = alt_acc_prox_grad.alternating_pgd(
                    U, V, 
                    lambda U, V: regularized_cost(U, V.T, X, Y, Lx, Ly, lamb, Omega),
                    lambda U, V: grad_cost_U(U, V.T, X, Y, Lx, Ly, lamb, Omega),
                    lambda U, V: grad_cost_V(U, V.T, X, Y, Lx, Ly, lamb, Omega).T, # note transpose
                    math_util.indicate_positive,
                    math_util.proj_nonnegative,
                    tol,
                    alt_tol,
                    max_outer_iter,
                    max_inner_iter,
                    max_line_iter,
                    calculate_cost)
    
    print("Counts:", counts)
    print("Avg times", np.divide(times, counts))
    print("Total times", times)


    return U, V, costs


def P_Omega(X, Omega):
    # print("P_omega")
    X[Omega.toarray()==1] = 0
    return X

'''
        gU=2*(P_Omega(U*V'*X-Y,Omega)*X'*V +...
              lambda*(Ly'*U*V'*Lx' + Ly'*Ly*U*V' + ...
                      U*V'*Lx'*Lx + Ly*U*V'*Lx)*V);
'''
def grad_cost_U(U, V, X, Y, Lx, Ly, lamb, Omega):
    global counts
    counts[1] += 1
    start_time = time.time()

    

    result = U @ (V.T @ Lx.T @ V)
    result = result + Ly @ U @ (V.T @ V)
    result = Ly.T @ result
    result = result + U @ (V.T @ Lx.T@ Lx @ V)
    result = result + Ly @ U @ (V.T @ Lx @ V)
    result = lamb * result
    result = 2* (result + P_Omega(U @ (V.T @ X) - Y, Omega) @ (X.T @ V))

    times[1] += time.time() - start_time

    return result


'''
        gV=2*(X*P_Omega(U*V'*X-Y,Omega)'*U + ...
              lambda*(Lx*V*U'*Ly + V*U'*Ly'*Ly +...
                      Lx'*Lx*V*U' + Lx'*V*U'*Ly')*U);
'''
def grad_cost_V(U ,V ,X, Y, Lx, Ly, lamb, Omega):
    global counts
    counts[2] += 1
    start_time = time.time()

    result = Lx @ V @ (U.T @ Ly @ U)
    result = result + V @ (U.T @ Ly.T @ Ly @ U)
    result = result + Lx.T @ Lx @ V @ (U.T @ U)
    result = result + Lx.T @ V @ (U.T @ Ly.T @ U)
    result = lamb * result
    result = 2* (result + X @ (P_Omega(U @ (V.T @ X) - Y, Omega).T @ U))

    times[2] += time.time() - start_time

    return result


def regularized_cost(U, V, X, Y, Lx, Ly, lamb, Omega):
    counts[0] += 1
    start_time = time.time()
    
    # print("regularized_cost", U.shape, V.shape, X.shape, Y.shape, Lx.shape, Ly.shape, Omega.shape)
    result = np.linalg.norm(P_Omega(U @ (V.T @ X) - Y, Omega), ord='fro')**2
    result = result + lamb * math_util.factorized_sum_frobenius_sq_j_einsum(Ly @ U, V.T, U, V.T @ Lx.T)
    times[0] += time.time() - start_time

    return result

def loss(U, V, X, Y, Omega):
    loss = np.linalg.norm(P_Omega(U @ (V.T @ X) - Y, Omega), ord='fro')**2
    return loss

def regularization(U, V, Lx, Ly, lamb):
    regularization = math_util.factorized_sum_frobenius_sq_j_einsum(Ly @ U, V.T, U, V.T @ Lx.T)
    return regularization

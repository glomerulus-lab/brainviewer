import numpy as np
from typing import Callable
import sys, inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
import util.math_util as math_util
line_count = 0

def alternating_pgd(U, V, 
                    cost_func,
                    grad_func_U,
                    grad_func_V,
                    indicator_func,
                    projection_func,
                    tol=1e-10,
                    alt_tol=1e-5,
                    max_outer_iter = 10,
                    max_inner_iter = 10,
                    max_line_iter = 100,
                    calculate_cost = False
                    ):

    costs = [cost_func(U, V)]

    U_k = U
    V_k = V
    k = 0
    prev_fro_norm = -2 * tol
    while(k < max_outer_iter):
        k+=1
        prev_U = U_k
        prev_V = V_k

        # Prepare functions in terms of V_k
        cost_V_k = lambda V_k: cost_func(U_k, V_k)
        grad_V_k = lambda V_k: grad_func_V(U_k, V_k)

        # Perform PGD on V_k
        V_k = acc_prox_grad_method( V_k, 
                                    cost_V_k, 
                                    grad_V_k, 
                                    indicator_func, 
                                    projection_func,
                                    tol=alt_tol, 
                                    max_iter=max_inner_iter, 
                                    max_line_iter=max_line_iter,
                                    gamma=0.1)

        if(indicator_func(V_k) > 0):
            print("Error: indicator function for V true. Exitting...")
            exit()


        # Prepare functions in terms of U_k
        cost_U_k = lambda U_k: cost_func(U_k, V_k)
        grad_U_k = lambda U_k: grad_func_U(U_k, V_k)

        #Perform PGD on U_k
        U_k = acc_prox_grad_method( U_k, 
                                    cost_U_k, 
                                    grad_U_k, 
                                    indicator_func, 
                                    projection_func,
                                    tol=alt_tol, 
                                    max_iter=max_inner_iter, 
                                    max_line_iter=max_line_iter,
                                    gamma=0.1)

        if(indicator_func(U_k) > 0):
            print("Error: indicator function for U true. Exiting...")
            exit()



        
        
        if(calculate_cost):
            cost = cost_func(U_k, V_k)
            print(k, cost, end='\r', flush=True)
            costs.append(cost)
            
        fro_norm_sq = np.trace(V_k @ V_k.T @ U_k.T @ U_k)
        if (math_util.factorized_difference_frobenius_sq(U_k, V_k, prev_U, prev_V) / fro_norm_sq < tol**2):
            break
    
    print()
    if(k < max_outer_iter):
        print("Tolerance reached.")

    print("Line count:", line_count)
    return U_k, V_k, costs
             




# acc_prox_grad_method from below:
# https://github.com/harrispopgen/mushi/blob/master/mushi/optimization.py
# https://github.com/harrispopgen/mushi/blob/master/LICENSE
def acc_prox_grad_method(x: np.ndarray,  # noqa: C901
                         g: Callable[[np.ndarray], np.float64],
                         grad_g: Callable[[np.ndarray], np.float64],
                         h: Callable[[np.ndarray], np.float64],
                         prox: Callable[[np.ndarray, np.float64], np.float64],
                         tol: np.float64 = 1e-10,
                         max_iter: int = 100,
                         s0: np.float64 = 1,
                         max_line_iter: int = 100,
                         gamma: np.float64 = 0.5,
                         verbose: bool = False) -> np.ndarray:
    r"""Nesterov accelerated proximal gradient method with backtracking line
    search [1]_.

    The optimization problem solved is:

    .. math::
        \min_x g(x) + h(x)

    where :math:`g` is differentiable, and the proximal operator for :math:`h`
    is available.

    Args:
        x: initial point
        g: differentiable term in objective function
        grad_g: gradient of g
        h: non-differentiable term in objective function
        prox: proximal operator corresponding to h
        tol: relative tolerance in objective function for convergence
        max_iter: maximum number of proximal gradient steps
        s0: initial step size
        max_line_iter: maximum number of line search steps
        gamma: step size shrinkage rate for line search
        verbose: print convergence messages

    Returns:
        solution point

    References
    ----------
    .. [1] https://people.eecs.berkeley.edu/~elghaoui/Teaching/EE227A/lecture18.pdf

    """
    # initialize step size
    s = s0
    # initialize momentum iterate
    q = x
    # initial objective value
    f = g(x) + h(x)
    if verbose:
        print(f'initial objective {f:.6e}', flush=True)
    for k in range(1, max_iter + 1):
        # evaluate differtiable part of objective at momentum point
        g1 = g(q)
        grad_g1 = grad_g(q)
        if not np.all(np.isfinite(grad_g1)):
            raise RuntimeError(f'invalid gradient at iteration {k + 1}: '
                               f'{grad_g1}')
        # store old iterate
        x_old = x
        # Armijo line search
        
        #note: for better performance, do not reset step size
        # s = s0
        
        for line_iter in range(max_line_iter):
            global line_count
            line_count += 1
            # new point via prox-gradient of momentum point
            x = prox(q - s * grad_g1, s)
            # G_s(q) as in the notes linked above
            G = (1 / s) * (q - x)
            # test g(q - sG_s(q)) for sufficient decrease
            if g(q - s * G) <= (g1 - s * (grad_g1 * G).sum()
                                + (s / 2) * (G ** 2).sum()):
                # Armijo satisfied
                break
            else:
                # Armijo not satisfied
                s *= gamma  # shrink step size
                # print("line search iter: ", line_iter)

        # update momentum point
        q = x + ((k - 1) / (k + 2)) * (x - x_old)

        if line_iter == max_line_iter - 1:
            print('warning: line search failed', flush=True)
            s = s0
        if not np.all(np.isfinite(x)):
            print('warning: x contains invalid values', flush=True)
        # terminate if objective function is constant within tolerance
        f_old = f
        f = g(x) + h(x)
        rel_change = np.abs((f - f_old) / f_old)
        if verbose:
            print(f'iteration {k}, objective {f:.3e}, '
                  f'relative change {rel_change:.3e}',
                  end='        \r', flush=True)
        if rel_change < tol:
            if verbose:
                print(f'\nrelative change in objective function {rel_change:.2g} '
                      f'is within tolerance {tol} after {k} iterations',
                      flush=True)
                print("@@@@                       line search tolerance reached")
            break
        if k == max_iter:
            if verbose:
                print(f'\nmaximum iteration {max_iter} reached with relative '
                      f'change in objective function {rel_change:.2g}',
                      flush=True)

    return x

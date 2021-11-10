import numpy as np
from jax import jit
import jax.numpy as jnp
from jax.config import config
config.update("jax_enable_x64", True)

# ||YZ+WH||F^2
@jit
def factorized_sum_frobenius_sq_j_einsum(W, H, Y, Z):

    #path = np.einsum_path("ij,kj,lk,li",H,H,W,W,optimize="optimal")
    # trace1 = np.trace(H @ H.T @ W.T @ W)
    trace1 = jnp.einsum("ij,kj,lk,li",H,H,W,W,optimize='greedy')
    # trace2 = np.trace(Z @ Z.T @ Y.T @ Y)
    trace2 = jnp.einsum("ij,kj,lk,li",Z,Z,Y,Y,optimize='greedy')
    # trace3 = np.trace(H @ Z.T @ Y.T @ W)
    trace3 = jnp.einsum("ij,kj,lk,li",H,Z,Y,W,optimize='greedy')
    result = trace1 + trace2 + 2*trace3
    return result

@jit
def factorized_difference_frobenius_sq_j_einsum(W, H, Y, Z):

    #path = np.einsum_path("ij,kj,lk,li",H,H,W,W,optimize="optimal")
    # trace1 = np.trace(H @ H.T @ W.T @ W)
    trace1 = jnp.einsum("ij,kj,lk,li",H,H,W,W,optimize='greedy')
    # trace2 = np.trace(Z @ Z.T @ Y.T @ Y)
    trace2 = jnp.einsum("ij,kj,lk,li",Z,Z,Y,Y,optimize='greedy')
    # trace3 = np.trace(H @ Z.T @ Y.T @ W)
    trace3 = jnp.einsum("ij,kj,lk,li",H,Z,Y,W,optimize='greedy')
    result = trace1 + trace2 - 2*trace3


    return result


# def factorized_sum_frobenius_sq_einsum(W, H, Y, Z):

#     #path = np.einsum_path("ij,kj,lk,li",H,H,W,W,optimize="optimal")
#     # trace1 = np.trace(H @ H.T @ W.T @ W)
#     trace1 = np.einsum("ij,kj,lk,li",H,H,W,W,optimize='optimal')
#     # trace2 = np.trace(Z @ Z.T @ Y.T @ Y)
#     trace2 = np.einsum("ij,kj,lk,li",Z,Z,Y,Y,optimize='optimal')
#     # trace3 = np.trace(H @ Z.T @ Y.T @ W)
#     trace3 = np.einsum("ij,kj,lk,li",H,Z,Y,W,optimize='optimal')
#     result = trace1 + trace2 + 2*trace3
#     return result


# def factorized_difference_frobenius_sq_einsum(W, H, Y, Z):

#     #path = np.einsum_path("ij,kj,lk,li",H,H,W,W,optimize="optimal")
#     # trace1 = np.trace(H @ H.T @ W.T @ W)
#     trace1 = np.einsum("ij,kj,lk,li",H,H,W,W,optimize='optimal')
#     # trace2 = np.trace(Z @ Z.T @ Y.T @ Y)
#     trace2 = np.einsum("ij,kj,lk,li",Z,Z,Y,Y,optimize='optimal')
#     # trace3 = np.trace(H @ Z.T @ Y.T @ W)
#     trace3 = np.einsum("ij,kj,lk,li",H,Z,Y,W,optimize='optimal')
#     result = trace1 + trace2 - 2*trace3


#     return result


# def factorized_sum_frobenius_sq_einsum(W, H, Y, Z):

#     #path = np.einsum_path("ij,kj,lk,li",H,H,W,W,optimize="optimal")
#     # trace1 = np.trace(H @ H.T @ W.T @ W)
#     trace1 = np.einsum("ij,kj,lk,li",H,H,W,W,optimize='optimal')
#     # trace2 = np.trace(Z @ Z.T @ Y.T @ Y)
#     trace2 = np.einsum("ij,kj,lk,li",Z,Z,Y,Y,optimize='optimal')
#     # trace3 = np.trace(H @ Z.T @ Y.T @ W)
#     trace3 = np.einsum("ij,kj,lk,li",H,Z,Y,W,optimize='optimal')
#     result = trace1 + trace2 + 2*trace3
#     return result

# # ||YZ+WH||F^2 using trace
# def factorized_sum_frobenius_sq(W, H, Y, Z):

#     trace1 = np.trace(np.linalg.multi_dot((H, H.T, W.T, W)))
#     trace2 = np.trace(np.linalg.multi_dot((Z, Z.T, Y.T, Y)))
#     trace3 = np.trace(np.linalg.multi_dot((H, Z.T, Y.T, W)))
#     result = trace1 + trace2 + 2*trace3
#     return result

# ||YZ-WH||F^2 using trace
def factorized_difference_frobenius_sq(W, H, Y, Z):

    trace1 = np.trace(np.linalg.multi_dot((H, H.T, W.T, W)))
    trace2 = np.trace(np.linalg.multi_dot((Z, Z.T, Y.T, Y)))
    trace3 = np.trace(np.linalg.multi_dot((H, Z.T, Y.T, W)))
    result = trace1 + trace2 - 2*trace3
    return result

# grad_W( ||YZ-WH||F^2 )
@jit
def grad_factorized_difference_frobenius_sq(W, H, Y, Z):
    # print("grad_frobenius_squared", W.shape, H.shape, Y.shape, Z.shape)
    return 2 * (W @ (H @ H.T) - (Y @ (Z @ H.T)) )

# Project Matrix X to nonnegative by setting all negative elements to 0.
# step size parameter 's' ignored (required for use as prox argument in for acc_prox_grad_method)

def proj_nonnegative(X, s=None): 
    return X - X*(X<0)

# Return maximum cost if X has any elements < 0

def indicate_positive(X):
    if(np.min(X) < 0):
        return np.inf
    else:
        return 0

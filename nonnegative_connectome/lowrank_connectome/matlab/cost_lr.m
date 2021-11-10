% Computes the cost of the low-rank solution
% Inputs:
%   W: the low-rank solution as a 2x1 cell
%   X: a matrix of sources
%   Y: a matrix of targets
%   Lx,Ly: Laplace matrices in the corresponding spaces
%   Omega: a mask matrix
%   lambda: a regularisation parameter
%
% Output:
%   J: the total cost

function [J] = cost_lr(W,X,Y,Lx,Ly,Omega,lambda)

% Norm of misfit
Jp = P_Omega(Y - W{1}*(W{2}'*X), Omega);
Jp = norm(Jp, 'fro')^2;

% Norm of Laplace -- compute in low-rank form
[~,J] = qr([W{1}, Ly*W{1}],0);
J = J*[Lx*W{2}, W{2}]';
J = norm(J, 'fro')^2;

lambda = lambda*size(X,2)/size(Lx,1);

J = 0.5*(lambda*J + Jp);

end


function Y = P_Omega(Y, Omega)
    Y(Omega ~= 0) = 0;
end



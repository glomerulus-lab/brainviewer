function [x,pcgiters] = greedy_lr_solve(Amult, Asolve, y, tol, varargin)
% [x,pcgiters] = greedy_lr_solve(Amult, Asolve, y, tol, varargin)
% Greedy low-rank solution algorithm with Galerkin update
%
% Inputs:
% Amult is a {2,R} cell of matrices, either sparse(n x n) or dense columns 
% X of a low-rank XX^T matrix.
% Asolve = @(i,s,y,x_prev)Asolve(i,s,y,x_prev) is a solution routine, where
%   i: block number (1 or 2)
%   s: a 1 x R vector of shifts (multipliers)
%   y: a n(i) x 1 RHS vector
%   x_prev: a n(i) x 1 initial guess vector
% The procedure should solve Bx=y, where B = sum_{k=1}^R A{i,k}*s(k).
% tol is the relative stopping tolerance
%
% Additional arguments can be given in the form 'arg1', value1, and so on.
% Admissible parameters are the following:
%       'rmax': maximal rank (default 100)
%       'nswp': maximal number of ALS sweeps for each rank-1 term (def. 30)
%
% Outputs:
% x is a {2,1} cell, each cell contains n x r matrix of factors in the
% corresponding dimension.
% pcgiters is a vector of PCG iterations carried out in each greedy step.

rmax = 100; % maximal rank
nswp = 30; % maximal number of ALS sweeps for z. 

for i=1:2:numel(varargin)
    switch(lower(varargin{i}))
        case 'rmax'
            rmax = varargin{i+1};
        case 'nswp'
            nswp = varargin{i+1};
        otherwise
            error('unknown parameter %s', varargin{i});
    end
end

pcgiters = zeros(rmax,1);

Ra = size(Amult,2);
n = cellfun(@(y)size(y,1), y);

% Determine the device we work on
gpu = false;
if (isa(Amult{1,1}, 'gpuArray'))
    gpu = true;
end

% Initialize x with 0 and the error with a random vector
x = cell(2,1);
if (gpu)
    x{1} = gpuArray.zeros(n(1),0);
    x{2} = gpuArray.zeros(n(2),0);
    z1 = gpuArray.randn(n(1),1);
    z2 = gpuArray.randn(n(2),1);
else
    x{1} = zeros(n(1), 0);
    x{2} = zeros(n(2), 0);
    z1 = randn(n(1), 1);
    z2 = randn(n(2), 1);
end
X_x = [];
% Storage for Galerkin matrix between the low-rank factors
A_x = cell(2,Ra);

for r=1:rmax        
    max_z = 0;
    % rank-1 ALS for the error
    x1 = x{1};
    x{1} = x{1}*X_x; % we need the actual solution
    t1 = tic;
    for swp=1:nswp
        z = z1/norm(z1);
        z2 = als_z(2,Amult,Asolve,x,y,z,z2, gpu);
        z = z2/norm(z2);
        z1 = als_z(1,Amult,Asolve,x,y,z,z1, gpu);
        dz = abs(norm(z1)/norm(z2)-1);
        if (dz<0.1) % z only enriches the basis, this should be ok
            break;
        end
    end
    fprintf('residual problem took %g sec.\n', toc(t1));
    x{1} = x1;
    
    max_z = max([max_z, norm(z1), norm(z2)]);
    % Enrich the solution
    if (r<min(n))
        [z,~] = qr([x{1}, z1], 0);
        z = z(:,end);
        x{1} = [x{1}, z];
        [z,~] = qr([x{2}, z2], 0);
        z = z(:,end);
        x{2} = [x{2}, z];
    end
        
    % Galerkin system for the rxr matrix between the factors
    t1 = tic;
    for k=1:Ra
        for i=1:2   % two dimensions
            % X basis is not discarded, hence the top left of A_x is preserved
            xnew = x{i}(:,r);
            xprev = x{i}(:,1:r-1);
            if (issparse(Amult{i,k}))
                % the matrix factor can be either sparse matrix ...
                ynew = Amult{i,k}*xnew;
                A_x{i,k} = blkdiag(A_x{i,k},  xnew'*ynew);
                A_x{i,k}(1:r-1,r) = xprev'*ynew;
            else
                % ... or columns of low-rank matrix
                ynew = Amult{i,k}'*xnew;
                A_x{i,k} = blkdiag(A_x{i,k}, ynew'*ynew);
                z = xprev'*Amult{i,k};
                A_x{i,k}(1:r-1,r) = z*ynew;
            end
            A_x{i,k}(r,1:r-1) = A_x{i,k}(1:r-1,r)';
        end
    end
    fprintf('matrix projection took: %g sec.\n', toc(t1));    
    t1 = tic;
    % concat individual matrix factors into a dense matrix for more freedom
    % in blocking
    Axf1 = vertcat(A_x{1,:}); % size rx1'*ra, rx1
    Axf2 = horzcat(A_x{2,:}); % size rx2', rx2*ra
    Axf2 = reshape(Axf2, r*r, Ra);
    Axf2 = Axf2.';
    Axf2 = reshape(Axf2, Ra*r, r);
    fprintf('+permute took %g sec.\n', toc(t1));        
    t1 = tic;   
    % Right hand side and initial guess
    Y_x = (x{1}'*y{1})*(x{2}'*y{2}).';
    Y_x = Y_x(:);
    X_x_prev = blkdiag(X_x, 0);
    X_x_prev = reshape(X_x_prev, r*r, 1);
        
    % A homebrew pcg using only ordinary matrices that should port
    % transparently onto a GPU
    [X_x,ITER] = pcg_2d(Axf1,Axf2, Y_x, tol*0.5, 2000, X_x_prev);

    pcgiters(r) = ITER;
    % Check the convergence
    dx = norm(X_x - X_x_prev, 'fro')/norm(X_x, 'fro');
    fprintf('+solve took %g sec and %d iters\n', toc(t1), ITER);
    
    max_z = max_z/norm(X_x,'fro');
    
    X_x = reshape(X_x, r, r);

    % Sometimes the error does not improve the solution anymore, discard it
    if (max_z>1e2*dx)
        if (gpu)
            z1 = gpuArray.randn(n(1), 1);
        else
            z1 = randn(n(1), 1);
        end
        warning('Z stagnated, refreshing to random...');
    end
    
    if (r>1)
        fprintf('\nr=%d, max_z=%3.3e, dx=%3.3e, als took %d sweeps for d|z|=%3.3e\n', r, max_z, dx, swp, dz);
        if (dx<tol)&&(max_z<tol)
            break;
        end
    end
end

x{1} = x{1}*X_x;
end


% rank-1 als for error
function [z] = als_z(i,Amult,Asolve,x,y,z_other,z, gpu)
Ra = size(Amult,2);
% Reduced matrices for another block (just shifts for rank-1)
if (gpu)
    ZAZ = gpuArray.zeros(1,Ra);
else
    ZAZ = zeros(1,Ra);
end
for k=1:Ra
    if (issparse(Amult{2-i+1,k}))
        ZAZ(k) = z_other'*(Amult{2-i+1,k}*z_other);
    else
        tmp = Amult{2-i+1,k}'*z_other;
        ZAZ(k) = tmp'*tmp;
    end
end
% reduced residual
Res_z = y{i}*(z_other'*y{2-i+1}).';
if (~isempty(x{1}))
    for k=1:Ra
        if (issparse(Amult{2-i+1,k}))
            ZAX = (z_other'*Amult{2-i+1,k})*x{2-i+1};
        else
            tmp = z_other'*Amult{2-i+1,k};
            ZAX = tmp*(Amult{2-i+1,k}'*x{2-i+1});
        end
        tmp = x{i}*ZAX.';
        if (issparse(Amult{i,k}))
            Res_z = Res_z - Amult{i,k}*tmp;
        else
            Res_z = Res_z - Amult{i,k}*(Amult{i,k}'*tmp);
        end
    end
end
% Solve the shifted system
z = Asolve(i,ZAZ,Res_z,z);
end



% PCG with the matvec restricted to A1*v*A2
function [x,i]=pcg_2d(A1,A2,y,tol,maxit,x, precfun)
m = size(A1,2);
rho = 1;
normy = norm(y);
if (nargin<7)
    precfun = @(x)x;
end
% initial resid
r = reshape(x, m, m);
r = A1*r;
r = reshape(r, m, []);
r = r*A2;
r = reshape(r, [], 1);
r = y - r;
for i=1:maxit
    z = precfun(r);
    rho1 = rho;
    rho = r'*z;
    if (i==1)
        p = z;
    else
        beta = rho/rho1;
        p = z + beta * p;
    end
    q = reshape(p, m, m);
    q = A1*q;
    q = reshape(q, m, []);
    q = q*A2;
    q = reshape(q, [], 1);
    pq = p'*q;
    alpha = rho / pq;
    x = x + alpha * p;             % form new iterate
    r = r - alpha * q;
    resid = norm(r)/normy;
    if (resid<tol)
        break;
    end
end
fprintf('pcg converged in %d iterations to resid=%3.3e\n', i, resid);
end

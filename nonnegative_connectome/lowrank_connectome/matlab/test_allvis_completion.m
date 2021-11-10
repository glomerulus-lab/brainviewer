function test_allvis_completion(testname, lambda,tol,rmax,gpu)
% Tests different completion problems
% Inputs:
%   testname ('test', 'top_view' or 'flatmap')
%   lambda: regularisation parameter (before normalisation)
%   tol: stopping tolerance in the greedy solver
%   rmax: maximal solution rank
%   gpu: if true, compute dense linear algebra on GPU
%
% When the test completes, all variables are copied into the main Matlab
% workspace:
%   W: the solution stored in a 2x1 cell array
%   pcgiters: numbers of PCG iters in each greedy step
%   resid: randomized estimate of the final residual
%   ttimes: CPU time
% These variables are also saved into a file ../data/testname_solution.mat

if (nargin<1)||(isempty(testname))
    testname = input('Which test to run (test, top_view, flatmap)? ', 's');
    if (isempty(testname))
        testname = 'test'
    end
end
if (nargin<2)||(isempty(lambda))
    lambda = input('Regularisation parameter? ');
    if (isempty(lambda))
        lambda = 100
    end
end
if (nargin<3)||(isempty(tol))
    tol = input('Stopping tolerance? ');
    if (isempty(tol))
        tol = 1e-7
    end
end
if (nargin<4)||(isempty(rmax))
    rmax = input('Maximal rank? ');
    if (isempty(rmax))
        rmax = 50
    end
end
if (nargin<5)||(isempty(gpu))
    gpu = input('Use gpu? ');
    if (isempty(gpu))
        gpu = false
    end
end


load(['../data/' testname '_matrices.mat'])

n = size(Ly,1); % These should come from the file
m = size(Lx,1);
r = size(X,2);

X = full(X);
Y = full(Y);
Omega = full(Omega);

Omega = 1-Omega; % File contains the complement
lambda = lambda*r/m; % dimensionless reg param

if (gpu)
    I1 = gpuArray.speye(n);
    I2 = gpuArray.speye(m);
    
    Lx = gpuArray(Lx);
    Ly = gpuArray(Ly);
    Omega = gpuArray(Omega);
    Y = gpuArray(Y);
    X = gpuArray(X);
else
    I1 = speye(n);
    I2 = speye(m);
end

% Right hand side
G = {Omega.*Y; X};


Lx2 = Lx*Lx;
Ly2 = Ly*Ly;

% Matmult functions
Amult = cell(2,r+3);
Amult(:,1:3) = {2*Ly,       Ly2,       I1;
                lambda*Lx,  lambda*I2, lambda*Lx2}; 
            
% Completion terms
Om = cell(1,r);
for i=1:r
    Om{i} = spdiags(Omega(:,i),0,n,n);
    if (gpu)
        Om{i} = gpuArray(Om{i});
    end
    Amult{1,i+3} = Om{i};
    Amult{2,i+3} = X(:,i);
end

% Solve
t2=tic;
[W,pcgiters] = greedy_lr_solve(Amult, @(i,s,y,x)Asolve(i,s,y,x,Lx,Ly,lambda,X,Omega,n,m), G, tol, 'rmax', rmax);
ttimes = toc(t2);
fprintf('Elapsed time is %g sec.\n', ttimes);

% Estimate residual by random projection
if (gpu)
    R2 = gpuArray.randn(m, r);
    R1 = gpuArray.zeros(n, r);
else
    R2 = randn(m, r);
    R1 = zeros(n, r);
end
for i=1:r+3
    if (issparse(Amult{2,i}))
        R1 = R1 + (Amult{1,i}*W{1})*(R2'*(Amult{2,i}*W{2}))';
    else
        R1 = R1 + (Amult{1,i}*W{1})*((R2'*Amult{2,i})*(Amult{2,i}'*W{2}))';
    end
end
R1 = R1 - G{1}*(R2'*G{2})';
% R1 should be a good basis
[R1,~]=qr(R1, 0);
R2 = R2'*0;
for i=1:r+3
    if (issparse(Amult{2,i}))
        R2 = R2 + (R1'*(Amult{1,i}*W{1}))*(Amult{2,i}*W{2})';
    else
        R2 = R2 + (R1'*(Amult{1,i}*W{1}))*(Amult{2,i}*(Amult{2,i}'*W{2}))';
    end
end
R2 = R2 - (R1'*G{1})*G{2}';
[~,Rg]=qr(G{1},0);

resid = norm(R2, 'fro')/norm(G{2}*Rg.', 'fro');
fprintf('Randomized residual = %3.3e\n', resid);

W{1} = gather(W{1});
W{2} = gather(W{2});

save(['../data/' testname '_solution.mat']);

% Copy vars to main space
vars = whos;
for i=1:numel(vars)
    assignin('base', vars(i).name, eval(vars(i).name));
end
end



function [x]=Asolve(i,s,y,x,Lx,Ly,lambda,X,Omega,n,m)
gpu = isa(Lx, 'gpuArray');
switch(i)
    case 1
        if (gpu)
            I = gpuArray.speye(n);
        else
            I = speye(n);            
        end
        A = 2*Ly*s(1) + Ly*Ly*s(2) + I*s(3);
        % Completion terms
        Omega_S = Omega*s(4:end)';
        Omega_S = spdiags(Omega_S, 0, n, n);
        A = A + Omega_S;
        % Strangely, sparse LU is faster on CPU
        if (gpu)
            A = gather(A);
            y = gather(y);
        end
        x = A\y;
        if (gpu)
            x = gpuArray(x);
        end
    case 2
        if (gpu)
            I = gpuArray.speye(m);
        else
            I = speye(m);
        end
        A = s(1)*Lx + s(2)*I + s(3)*Lx*Lx;
        A = A*lambda;
        % X updated with projected Omega
        Y = X*diag(sqrt(s(4:end)));
        % Sherman: inv(B) = inv(A) - inv(A)*X*inv(I+X'*inv(A)*X)*X'*inv(A)
        % s(3) should be 1 anyway
        assert(abs(s(3)-1)<1e-12);
        
        Y2 = [y, Y];
        if (gpu)
            Y2 = gather(Y2);
            A = gather(A);
        end
        x = A\Y2;
        if (gpu)
            x = gpuArray(x);
        end
        
        AY = x(:,2:end);
        x = x(:,1);
        % Denominator
        if (gpu)
            K = gpuArray.eye(size(X,2));
        else
            K = eye(size(X,2));
        end
        K = K + Y'*AY;
        x = x - AY*(K\(AY'*y));
end
end


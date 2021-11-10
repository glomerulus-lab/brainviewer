% Plot full test solution
%
% Requires brewermap.m
% Colorbrewer colormaps
% https://www.mathworks.com/matlabcentral/fileexchange/45208-colorbrewer--attractive-and-distinctive-colormaps

close all

load ../data/test_matrices.mat
load ../data/test_solution.mat
W = W{1}*W{2}';

r = rank(W);
fprintf('rank of W: %d\n', r)

ylim_arr = [min(voxel_coords_target), max(voxel_coords_target)];
xlim_arr = [min(voxel_coords_source), max(voxel_coords_source)];

set(0, 'DefaultAxesFontSize', 14);

% True kernel
figure(1);
imagesc(voxel_coords_source, voxel_coords_target, W_true);
map = brewermap(13, 'Reds');
colormap(map)
colorbar
ylim(ylim_arr)
xlim(xlim_arr)
title('W_{true}')
print('-dpng', '../data/sol_test_true.png')

% Completion kernel
figure(2);
imagesc(voxel_coords_source, voxel_coords_target, W);
map = brewermap(13, 'Reds');
colormap(map)
colorbar
draw_inj(X, voxel_coords_source);
ylim(ylim_arr)
xlim(xlim_arr)
title(sprintf('W_{%d}', r))
print('-dpng', sprintf('../data/sol_test_r_%d.png', r))

% Omega=0
if (exist('W_omega0'))
    figure(3);
    imagesc(voxel_coords_source, voxel_coords_target, W_omega0);
    map = brewermap(13, 'Reds');
    colormap(map)
    colorbar
    draw_inj(X, voxel_coords_source);
    ylim(ylim_arr)
    xlim(xlim_arr)
    title('\Omega = 1')
    print('-dpng', '../data/sol_test_omega0.png')
else
    warning('No solution W_omega0 found, this needs to be created in a test with Omega being all ones');
end

% lambda=0 (pinv)
W_lambda0 = Y*pinv(X);
figure(4);
imagesc(voxel_coords_source, voxel_coords_target, W_lambda0);
map = brewermap(13, 'Reds');
colormap(map)
colorbar
draw_inj(X, voxel_coords_source);
ylim(ylim_arr)
xlim(xlim_arr)
title('\lambda = 0')
print('-dpng', '../data/sol_test_lambda0.png')

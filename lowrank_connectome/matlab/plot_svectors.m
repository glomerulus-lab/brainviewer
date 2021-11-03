% Plot dominant singular vectors
%
% Requires brewermap.m
% Colorbrewer colormaps
% https://www.mathworks.com/matlabcentral/fileexchange/45208-colorbrewer--attractive-and-distinctive-colormaps

close all;

% Choose the solution
testname = input('Enter test name to draw (top_view, flatmap): ', 's');
if (isempty(testname))
    testname = 'top_view'
end

% Number of singular vectors
Nv = 6;

load(['../data/' testname '_matrices.mat']);
load(['../data/' testname '_solution.mat']);


[Q1,R1]=qr(W{1},0);
[Q2,R2]=qr(W{2},0);
[u,S,v]=svd(R1*R2');
Q1 = Q1*u;
Q2 = Q2*v;
S = diag(S);

for i=1:Nv
    % Plot scaled (U*S) vectors in the first figure.
    % We also correct the phase such that the maximal element is positive
    figure(1);
    [~,j] = max(abs(Q1(:,i)));
    sgn = 1/sign(Q1(j,i));
    fprintf('SV %d: %1.3g\n', i, S(i));
    new_image = ...
        map_to_grid(Q1(:,i)*sgn * S(i), voxel_coords_target, view_lut, ...
                    false);
    imagesc(new_image, 'alphadata', ~isnan(new_image));
    set(gca, 'xtick', [])
    set(gca, 'ytick', [])
    if i == 1
        map = brewermap(13,'Reds');
    else
        v = max(abs(caxis()));
        caxis([-v, v]);
        map = flipud(brewermap(13,'RdBu'));
    end
    colormap(map)
    c = colorbar;
    drawnow;
    if (strcmp(view, 'top_view'))
        c.FontSize = 14;
        daspect([1,1.6,1])
        ylim([40 270])
        xlim([6 280])
        alim = xlim();
        x_scale = ( alim(2) - alim(1) ) / (280 - 130);
    else
        c.FontSize = 12;
        daspect([1 1 1])
        xlim([20 660]);
        alim = xlim();
        x_scale = ( alim(2) - alim(1) ) / (660 - 350);
    end
    p1 = get(figure(1),'position');
    p1 = [p1(1), p1(2), x_scale * p1(3), p1(4)];
    set(figure(1), 'position', p1);

    fn1 = sprintf('../tex/%s_US_%d.png', view, i);
    print(gcf, '-dpng', fn1);
    system(sprintf('convert %s -trim %s', fn1, fn1))
    
    % Plot unscaled (V) vectors in the second figure
    figure(2);
    new_image = map_to_grid(Q2(:,i)*sgn, voxel_coords_source, view_lut, ...
                            false);
    imagesc(new_image, 'alphadata', ~isnan(new_image));
    set(gca, 'xtick', [])
    set(gca, 'ytick', [])
    if i == 1
        map = brewermap(13,'Reds');
    else
        v = max(abs(caxis()));
        caxis([-v, v]);
        map = flipud(brewermap(13,'RdBu'));
    end
    colormap(map)
    c = colorbar;
    if (strcmp(view, 'top_view'))
        c.FontSize = 14;
        daspect([1,1.6,1])
        ylim([40 270])
        xlim([130 280])
    else
        if i == 1
            set(c, 'YTickLabel', cellstr(num2str(reshape(get(c,'YTick'),[],1),'%0.3f')) )
        end
        c.FontSize = 12;
        daspect([1 1 1])
        xlim([350 660])
    end    
    drawnow;

    fn2 = sprintf('../tex/%s_V_%d.png', view, i);
    print(gcf, '-dpng', fn2);
    system(sprintf('convert %s -trim %s', fn2, fn2))
    
    if i < Nv
        close all
    end
end

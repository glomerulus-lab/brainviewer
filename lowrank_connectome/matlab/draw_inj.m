% Draw rectangles at the positions of injections (used in plot_test)

function draw_inj(X, coords)
    d=0.02;
    for i=1:size(X, 2)
        imin = min(coords(X(:, i) == 1));
        imax = max(coords(X(:, i) == 1));
        if i == 2 || i == 5  %% overlapping injections for this 
            ypos = 1 - d*2;
        else
            ypos = 1 - d;
        end
        h = rectangle('position', ...
                      [imin, ypos, imax-imin, d],...
                      'facecolor', [.4 .4 .4]);
    end
end


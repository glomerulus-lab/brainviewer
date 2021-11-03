% Interpolates discrete image vector from voxel onto integer nodes
% (used in plot_svectors)
% Inputs:
%   image_vec: an N x 1 image vector corresponding to nodes in voxel_coords
%   voxel_coords: an N x 2 matrix of coordinates
%   view_lut: reference output image
%   plotit: if true, plot the interpolation immediately
%
% Outputs:
%   new_image: the computed interpolation

function new_image = map_to_grid(image_vec, voxel_coords, view_lut, plotit)
new_image = nan(size(view_lut));
for i = 1:size(image_vec, 1)
    coord_i = num2cell(voxel_coords(i,:));
    new_image(coord_i{:}) = image_vec(i);
end

if (plotit)
    imagesc(new_image, 'alphadata', ~isnan(new_image));
    colorbar;
end
end

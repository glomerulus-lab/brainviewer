#!/bin/bash

# # Convert region overlay SVG to PNG
# convert cortical_map_top_down.svg -resize 200% cortical_map_top_down.png

# Remove whitespace from images
cd images


ffmpeg -start_number 0 -i "%05d.png" -c:v libx265 -crf 30 -b:v 0 -r 10 ../nonnegative_projection_anim.mp4

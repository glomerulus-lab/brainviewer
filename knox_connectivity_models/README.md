# knox_connectivity_models

To run the interactive brainviewer, add the following files:

- interactive_flat_map_animate.py
- cortical_map_top_down.png

to mouse_connectivity_models/examples/movie in https://github.com/AllenInstitute/mouse_connectivity_models after pulling the repository.

## interactive_flat_map_animate.py

Module to display an interactive topview or flatmap view of the mouse brain. Upon clicking the mouse brain, the related projection is diplayed.

Arguments:

- testname: "topview" or "flatmap"

Example Invocation:
```
python3 interactive_flat_map_animate.py flatmap
```
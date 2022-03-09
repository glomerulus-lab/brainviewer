# brainviewer

Pull from https://github.com/AllenInstitute/mouse_connectivity_models to get started.

If needed: wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh


To run the interactive brainviewer, first run set_up.py

Next, move or copy the following files and directories:
```
interactive_connectome.py
interactive_connectome2.py
cortical_map_top_down.png
transparent.png
colorbar.png
flatmapImages/*
topviewImages/*
```
to mouse_connectivity_models/examples/movie in https://github.com/AllenInstitute/mouse_connectivity_models after pulling the repository.


## interactive_connectome.py
Module to display an interactive topview or flatmap view of the mouse brain. Upon clicking the mouse brain, the related projection is **computed** and diplayed.

Arguments:
- testname: "topview" or "flatmap"

Example Invocation:
```
python3 interactive_connectome.py flatmap
```


## interactive_connectome2.py 
Module to display an interactive topview or flatmap view of the mouse brain. Upon clicking the mouse brain, the related projection is **uploaded** and diplayed. 

Arguments:
- testname: "topview" or "flatmap"

Example Invocation:
```
python3 interactive_connectome2.py flatmap
```


## Useful Modules

### connectome_img_generator.py
Module to create and download images for the flatmap and topview connectomes

Arguments:
- testname: "topview" or "flatmap"

Example Invocation:
```
python3 connectome_img_generator.py topview
```

```
...
├── src
│   ├── connectome_img_generator.py
│   └── generate_colorbar_fig.py
...
```
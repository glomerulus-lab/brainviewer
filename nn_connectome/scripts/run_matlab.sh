#!/bin/bash
cd ../lowrank_connectome/matlab
matlab -nodisplay -nosplash - nodesktop -r "${1}; exit"

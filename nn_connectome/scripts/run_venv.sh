#!/bin/sh

#Activate venv (needed in cluster)
. /cluster/research-groups/harris/stillwj3/connectome_venv/bin/activate

exec python "$@"

#!/bin/sh

#Jupyterlab extensions to install and then build
jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build
jupyter labextension install @jupyter-voila/jupyterlab-preview --no-build
jupyter lab build

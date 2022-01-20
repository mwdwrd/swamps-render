#!/usr/bin/python3
"""
This contains the core functionalities for:
1. Creating 3d .vox files from flat /png files
2. Converting those .vox files into .obj for usage in blender / other 3D programs.
"""

__author__ = "Matty Woodward"
__version__ = "1.0.0"
__license__ = "MIT"

import bpy
import os
import sys

# Specify the script to be executed
scriptFile = "blenderize.py"

# Check if script is executed in Blender and get absolute path of current folder
if bpy.context.space_data is not None:
    filesDir = os.path.dirname(bpy.context.space_data.text.filepath)
else:
    filesDir = os.path.dirname(os.path.abspath(__file__))

# Get scripts folder and add it to the search path for modules
cwd = os.path.join(filesDir, "./")
sys.path.append(cwd)

# Change current working directory to scripts folder
os.chdir(cwd)

# Compile and execute script file
file = os.path.join(cwd, scriptFile)
exec(compile(open(file).read(), scriptFile, 'exec'))

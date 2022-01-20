#!/usr/bin/env python3
"""

"""

__author__ = "Matty Woodward"
__version__ = "1.0.0"
__license__ = "MIT"

import argparse

def setup_parameters():
    parser = argparse.ArgumentParser(description='Chunks Engine')
    parser.add_argument("-a", "--artwork", help="artwork")
    return parser.parse_args()

def blender_parameters():
    parser = argparse.ArgumentParser(description='Chunks Engine')

    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]

    # add parser rules
    parser.add_argument('-a', '--artwork', help="artwork")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    print(parsed_script_args)
    return parsed_script_args

# import os
# import bpy
# import argparse

# def setup_parameters():
#     parser = argparse.ArgumentParser(description='Choadz Render Engine')

#     # get all script args
#     _, all_arguments = parser.parse_known_args()
#     double_dash_index = all_arguments.index('--')
#     script_args = all_arguments[double_dash_index + 1:]

#     # add parser rules
#     parser.add_argument('-c', '--choad', help="choad")
#     parser.add_argument('-r', '--render', help="render still")
#     parser.add_argument('-a', '--animation', help="render animation")
#     parsed_script_args, _ = parser.parse_known_args(script_args)
#     print(parsed_script_args)
#     return parsed_script_args


# def import_object_to_scene(filepath):
#     print("Importing {} to Scene".format(filepath))

#     scn = bpy.context.collection

#     # append object from .blend file
#     with bpy.data.libraries.load(filepath) as (data_from, data_to):
#         data_to.objects = data_from.objects

#     # link object to current scene
#     for obj in data_to.objects:
#         if obj is not None:
#             scn.objects.link(obj)

# def render_scene(renderFolder='output', file_name='render', resX=1080, resY=1080, resPercentage=100, animation=False, frame_end=None):
#     print('Rendering Chaod ' + str(file_name))

#     scn = bpy.data.scenes['Scene']
#     scn.render.resolution_x = resX
#     scn.render.resolution_y = resY
#     scn.render.resolution_percentage = resPercentage
#     if frame_end:
#         scn.frame_end = frame_end

#     # Check if script is executed inside Blender
#     if bpy.context.space_data is None:
#         # Specify folder to save rendering and check if it exists
#         render_folder = os.path.join(os.getcwd(), renderFolder)
#         if(not os.path.exists(render_folder)):
#             os.mkdir(render_folder)

#         if animation:
#             # Render animation
#             scn.render.filepath = os.path.join(render_folder, str(file_name))
#             bpy.ops.render.render(animation=True)
#         else:
#             # Render still frame
#             scn.render.filepath = os.path.join(render_folder, str(file_name) + '.png')
#             bpy.ops.render.render(write_still=True)


# def save_scene(fileLocation='output', file_name='render'):
#     print('Saving Choad' + str(file_name))

#     bpy.ops.wm.save_as_mainfile(filepath=os.path.join(fileLocation, str(file_name) + '.blend'), relative_remap=False)

# def open_file(file_path):
#     bpy.ops.wm.open_mainfile(filepath=file_path)
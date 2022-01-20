#!/usr/bin/python3
"""

"""

__author__ = "Matty Woodward"
__version__ = "1.0.0"
__license__ = "MIT"

import os
import bpy
from pathlib import Path
import glob
import os.path
import copy
import sys
import struct
import utils
import json
# from progressbar import progressbar

sys.path.append(os.path.realpath('..'))
dirname = os.path.dirname(__file__)

LINKED = False
SCALE_LENGTH = 0.1
LENGTH_UNIT = "METERS"
MASS_UNIT = "GRAMS"
RESIZE_RATIO = 1.05
VOX_SCALE = 0.025

class Vec3:
    def __init__(self, X, Y, Z):
        self.x, self.y, self.z = X, Y, Z
    
    def _index(self):
        return self.x + self.y*256 + self.z*256*256

class VoxelObject:
    def __init__(self, Voxels, Size):
        self.size = Size
        self.voxels = {}
        self.used_colors = []
        self.position = Vec3(0, 0, 0)
        self.rotation = Vec3(0, 0, 0)
        
        for vox in Voxels:
            #              x       y       z
            pos = Vec3(vox[0], vox[1], vox[2])
            self.voxels[pos._index()] = (pos, vox[3])
            
            if vox[3] not in self.used_colors:
                self.used_colors.append(vox[3])
               
    def getVox(self, pos):
        key = pos._index()
        if key in self.voxels:
            return self.voxels[key][1]
        
        return 0
    
    def compareVox(self, colA, b):
        colB = self.getVox(b)
        
        if colB == 0:
            return False
        return True

    def splitVoxelObject(self,zIndex):
        splitVoxels =[]
        for key in list(self.voxels):
            voxpos, colorId = self.voxels[key]
            if(voxpos.z >= zIndex):
                splitVoxels.append([voxpos.x,voxpos.y,voxpos.z,colorId])
                del self.voxels[key]

        return VoxelObject(splitVoxels,self.size)

    def generate(
        self,
        file_name,
        vox_size,
        materials,
        layerName,
        collections,
        palette
    ):

        objects = []
        self.materials = materials
        mesh_col, volume_col = collections

        if len(self.used_colors) == 0:  # Empty Object
            return

        # GROUPED COLORS
        for Col in self.used_colors: # for each color
            colobj = [] # list of voxels in this color
            colName = ''

            for key in self.voxels: # for each voxel
                pos, colID = self.voxels[key]
                x, y, z = pos.x, pos.y, pos.z

                material = make_material(palette[colID - 1])

                if colID == Col:
                    print('building mesh {}x{}y{}z'.format(x,y,z))
                    bpy.ops.mesh.primitive_cube_add(location=(x,y,z),size=1.05) #
                    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
                    bpy.ops.object.modifier_add(type='BEVEL')
                    bpy.context.object.modifiers["Bevel"].width = 0.1
                    bpy.context.object.modifiers["Bevel"].segments = 20
                    bpy.ops.object.modifier_apply(modifier="BEVEL")

                    new_obj = bpy.context.active_object # get the new object
                    new_obj.name = 'X' + str(x) + 'Y' + str(y) + 'Z' + str(z) # rename it
                    colName = material[1]
                    new_obj.data.materials.append(material[0])
                    colobj.append(new_obj) # add to list of objects in this color

            bpy.ops.object.select_all(action='DESELECT') # deselect all objects

            for obj in colobj: # for each object in this color
                obj.select_set(True) # select the object

            bpy.ops.object.join() # join all objects in this color
            objects.append(obj)
            obj.name = colName
            bpy.ops.object.select_all(action='DESELECT') # deselect all objects
            colobj = [] # Clear the list
        
        bpy.ops.object.select_all(action='DESELECT')

        for obj in objects:
            obj.select_set(True)  # Select all objects that were generated.

        # Sets the origin of object to be the same as in MagicaVoxel so that its location can be set correctly.
        bpy.context.scene.cursor.location = [0, 0, 0]

        # Set the cursor to the world center for correct scaling.
        center_origin()

        # Set scale and position.
        # bpy.ops.transform.translate(value=(self.position.x*vox_size, self.position.y*vox_size, self.position.z*vox_size))
        bpy.ops.transform.resize(value=(vox_size, vox_size, vox_size))

        return obj

def remove_default_bsdf(material):
    material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))

def gloss_plastic(hex, material, rgb_color, alpha):
    color_node = material.node_tree.nodes.get('Principled BSDF')
    color_node.inputs[0].default_value = (rgb_color[0], rgb_color[1], rgb_color[2], alpha)
    color_node.inputs[5].default_value = 0.1
    color_node.inputs[7].default_value = 1
    color_node.inputs[8].default_value = 0
    color_node.inputs[12].default_value = 0.8
    color_node.inputs[13].default_value = 0.03
    color_node.inputs['Alpha'].default_value = alpha
    print('Gloss Plastic Created: #{}'.format(hex))

def read_chunk(buffer):
    *name, h_size, h_children = struct.unpack('<4cii', buffer.read(12))
    name = b"".join(name)
    content = bytearray(buffer.read(h_size))
    return name, content

def read_content(content, size):
    out = content[:size]
    del content[:size]
    
    return out

def read_dict(content):
    dict = {}
    
    dict_size, = struct.unpack('<i', read_content(content, 4))
    for _ in range(dict_size):
        key_bytes, = struct.unpack('<i', read_content(content, 4))
        key = struct.unpack('<'+str(key_bytes)+'c', read_content(content, key_bytes))
        key = b"".join(key)
        
        value_bytes, = struct.unpack('<i', read_content(content, 4))
        value = struct.unpack('<'+str(value_bytes)+'c', read_content(content, value_bytes))
        value = b"".join(value)
        
        dict[key] = value
    
    return dict

def center_origin():
    bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
    bpy.context.scene.cursor.location = [0, 0, 0]
    bpy.context.scene.cursor.rotation_euler = [0, 0, 0]
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

def import_vox(path):

    def srgb_to_linear(r, g, b):
        def srgb(c):
            a = .055
            if c <= .04045:
                return c / 12.92
            else:
                return ((c+a) / (1+a)) ** 2.4
        return tuple(srgb(c) for c in (r, g, b))
    
    def RGB2sRGB2(RGBArray):
        new_rgb = RGBArray
        higher = (new_rgb > 0.0031308)
        lower = (new_rgb <= 0.0031308)
        new_rgb[higher] = (pow(new_rgb[higher], (1.0 / 2.4))) * 1.055 - 0.055
        new_rgb[lower] = 12.92 * new_rgb[lower]
        return new_rgb
    
    with open(path, 'rb') as file:
        file_name = os.path.basename(file.name).replace('.vox', '')
        file_size = os.path.getsize(path)
        
        palette = []
        materials = [[0.5, 0.0, 0.0, 0.0] for _ in range(255)]
        
        assert (struct.unpack('<4ci', file.read(8)) == (b'V', b'O', b'X', b' ', 150))
        assert (struct.unpack('<4c', file.read(4)) == (b'M', b'A', b'I', b'N'))
        N, M = struct.unpack('<ii', file.read(8))
        assert (N == 0)
        
        models = {}
        mod_id = 0
        layer_id = 0
        layers = {}
        transforms = {}
        groups = {}
        shapes = {}
        
        while file.tell() < file_size:
            name, content = read_chunk(file)

            if name == b'SIZE':
                x, y, z = struct.unpack('<3i', read_content(content, 12))
                size = Vec3(x, y, z)
            
            elif name == b'XYZI':
                voxels = []

                num_voxels, = struct.unpack('<i', read_content(content, 4))
                for voxel in range(num_voxels):
                    voxel_data = struct.unpack('<4B', read_content(content, 4))
                    voxels.append(voxel_data)
                
                model = VoxelObject(voxels, size)
                models[mod_id] = model
                mod_id += 1
            
            elif name == b'nTRN':
                id, = struct.unpack('<i', read_content(content, 4))

                grp = read_dict(content)                
                for key in grp:
                    value = grp[key]
                    layers[layer_id] = value.decode('utf-8')
                    layer_id += 1

                child_id, _, _, _, = struct.unpack('<4i', read_content(content, 16))
                transforms[child_id] = [Vec3(0, 0, 0), Vec3(0, 0, 0)]
                if id > 255: continue

                frames = read_dict(content)
                for key in frames:
                    if key == b'_r':
                        pass
                    
                    elif key == b'_t':
                        value = frames[key].decode('utf-8').split()
                        transforms[child_id][0] = Vec3(int(value[0]), int(value[1]), int(value[2]))
            
            elif name == b'nGRP':
                id, = struct.unpack('<i', read_content(content, 4))
                
                _ = read_dict(content)
                
                num_child, = struct.unpack('<i', read_content(content, 4))
                children = []
                
                for _ in range(num_child):
                    children.append(struct.unpack('<i', read_content(content, 4))[0])
                
                groups[id] = children


            elif name == b'nSHP':
                id, = struct.unpack('<i', read_content(content, 4))
                
                _ = read_dict(content)
                
                num_models, = struct.unpack('<i', read_content(content, 4))
                model_ids = []
                
                for _ in range(num_models):
                    model_ids.append(struct.unpack('<i', read_content(content, 4))[0])
                    _ = read_dict(content)
                
                shapes[id] = model_ids
      
            
            elif name == b'RGBA':
                for _ in range(255):
                    rgba = struct.unpack('<4B', read_content(content, 4))
                    palette.append([float(col)/255 for col in rgba])
                del content[:4]

            elif name == b'MATL':
                id, = struct.unpack('<i', read_content(content, 4))
                if id > 255: continue
                
                mat_dict = read_dict(content)
                
                for key in mat_dict:
                    value = mat_dict[key]
                    
                    mat = materials[id-1]
                    
                    if key == b'_type':
                        type = value
                    
                    if key == b'_rough':
                        materials[id-1][0] = float(value)
                    elif key == b'_metal' and type == b'_metal':
                        materials[id-1][1] = float(value)
                    elif key == b'_alpha' and type == b'_glass':
                        materials[id-1][2] = float(value)
                    elif key == b'_emit' and type == b'_emit':
                        materials[id-1][3] = float(value)
                    elif key == b'_flux':
                        materials[id-1][3] *= float(value)+1

    ### Apply Transforms ##
    for trans_child in transforms:
        trans = transforms[trans_child]

        if trans_child in shapes:
            shape_children = shapes[trans_child]

            for model_id in shape_children:
                models[model_id].position = trans[0]

    ## Create Collections ##
    collections = (None, None, None)
    main = bpy.data.collections.new(file_name)
    bpy.context.scene.collection.children.link(main)
    mesh_col = bpy.data.collections.new("Meshes")
    main.children.link(mesh_col)
    volume_col = bpy.data.collections.new("Volumes")
    main.children.link(volume_col)
    collections = (mesh_col, volume_col)

    for i in models:
        bodyMesh = models[i].generate(file_name, VOX_SCALE, materials, 'Model', collections, palette)

    return bodyMesh

def srgb_to_linear(r, g, b):
    def srgb(c):
        a = .055
        if c <= .04045:
            return c / 12.92
        else:
            return ((c+a) / (1+a)) ** 2.4
    return tuple(srgb(c) for c in (r, g, b))

def make_material(color):
    alpha = 1.0
    red, green, blue, alpha = color
    linear_color = srgb_to_linear(red, green, blue)
    rgb = '%02x%02x%02x' % (int(
        linear_color[0] * 255), int(linear_color[1] * 255), int(linear_color[2] * 255))
    material = bpy.data.materials.get(rgb)
    if material is None:
        material = bpy.data.materials.new(rgb)
        material.use_nodes = True
        bpy.ops.collection.create(name=rgb)
        gloss_plastic(rgb, material, linear_color, alpha)
    return material, rgb

def build_scene(file_name):
    template = 'templates/base.blend'
    bpy.ops.wm.open_mainfile(filepath=os.path.join(dirname, template))
    bpy.ops.collection.create(name=file_name)

def main():
    params = utils.blender_parameters()
    artwork = str(params.artwork)

    build_scene(artwork)
    import_vox('../output/{}/{}.vox'.format(artwork, artwork))

    outputPath = "../output/{}/{}".format(artwork, artwork)

    bpy.ops.wm.save_as_mainfile(filepath="{}.blend".format(outputPath), relative_remap=False)
    # bpy.ops.export_scene.gltf(filepath="{}.gltf".format(outputPath), export_cameras=False, export_apply=True, export_lights=False, use_selection=True, export_format="GLTF_EMBEDDED")
    # bpy.ops.export_scene.obj(filepath="{}.obj".format(outputPath), use_materials=True)

if __name__ == "__main__":
    main()
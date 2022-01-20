import bpy
import utils
import datetime
import materials
import shutil
import os
import sys
from pathlib import Path
import json

sys.path.append(os.path.realpath('..'))
dirname = os.path.dirname(__file__)

SIZE = [36, 36, 18]
LINKED = False
SCALE_LENGTH = 0.1
LENGTH_UNIT = "METERS"
MASS_UNIT = "GRAMS"
RESIZE_RATIO = 1.05

def find_choad(choad_id):
    with open(os.path.join(dirname, 'data/manifest.json')) as f:
        metadata = json.loads(f.read())
        for item in metadata:
            if float(item['tokenId']) == float(choad_id):
                return item

def get_template(choad_id):
    return 'templates/base.blend'

def build_scene(choad_id):
    baseType = get_template(choad_id)
    base = os.path.join(dirname, baseType)
    bpy.ops.wm.open_mainfile(filepath=base)
    bpy.data.scenes[0].render.engine = "CYCLES"
    bpy.context.preferences.addons[
        "cycles"
    ].preferences.compute_device_type = "CUDA"
    bpy.context.scene.unit_settings.scale_length = SCALE_LENGTH
    bpy.context.scene.unit_settings.length_unit = LENGTH_UNIT
    bpy.context.scene.unit_settings.mass_unit = MASS_UNIT
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    # bpy.context.scene.render.tile_x = 256
    # bpy.context.scene.render.tile_y = 256
    # bpy.context.preferences.addons["cycles"].preferences.get_devices()
    # print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
    # for d in bpy.context.preferences.addons["cycles"].preferences.devices:
    #     #print(d)
    #     d["use"] = 0
    #     if d["name"] == 'GeForce RTX 2070':
    #         d["use"] = 1
    #     #print(d["name"], d["use"])

    bpy.ops.collection.create(name=choad_id)

    library = os.path.join(dirname, 'templates/library.blend')
    with bpy.data.libraries.load(library, link=False) as (data_from, data_to):
        data_to.materials = [name for name in data_from.materials]

    bpy.data.images.load(os.path.join(
        dirname, "../input/" + str(choad_id) + ".png"))


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
        materials.gloss_plastic(rgb, material, linear_color, alpha)
    return material, rgb


def push_pixel(zIndex, xPos, yPos):
    i = zIndex
    block_size = 1
    step = SIZE[0]*2
    x = (xPos - step * zIndex) - (SIZE[0] - block_size*3) - 2
    y = yPos + block_size
    z = -((zIndex*2)*block_size) + (SIZE[2] - block_size)
    return x, y, z


def draw_pix(x, y, col, choad_id):
    material = make_material(col)
    step = (SIZE[0]*2)
    loop = 0

    if x <= step:
        loop = loop
    elif x >= step and x <= (step*2) - 1:
        loop = 1
    elif x >= step*2 and x <= (step*3) - 1:
        loop = 2
    elif x >= step*3 and x <= (step*4) - 1:
        loop = 3
    elif x >= step*4 and x <= (step*5) - 1:
        loop = 4
    elif x >= step*5 and x <= (step*6) - 1:
        loop = 5
    elif x >= step*6 and x <= (step*7) - 1:
        loop = 6
    elif x >= step*7 and x <= (step*8) - 1:
        loop = 7
    elif x >= step*8 and x <= (step*9) - 1:
        loop = 8
    elif x >= step*9 and x <= (step*10) - 1:
        loop = 9
    elif x >= step*10 and x <= (step*11) - 1:
        loop = 10
    elif x >= step*11 and x <= (step*12) - 1:
        loop = 11
    elif x >= step*12 and x <= (step*13) - 1:
        loop = 12
    elif x >= step*13 and x <= (step*14) - 1:
        loop = 13
    elif x >= step*14 and x <= (step*15) - 1:
        loop = 14
    elif x >= step*15 and x <= (step*16) - 1:
        loop = 15
    elif x >= step*16 and x <= (step*17) - 1:
        loop = 16
    elif x >= step*17 and x <= (step*18) - 1:
        loop = 17
    elif x >= step*18 and x <= (step*19) - 1:
        loop = 18
    elif x >= step*19 and x <= (step*20) - 1:
        loop = 19
    elif x >= step*20 and x <= (step*21) - 1:
        loop = 20
    elif x >= step*21 and x <= (step*22) - 1:
        loop = 21
    else:
        loop = 22

    [x, y, z] = push_pixel(loop, x, y)

    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    bpy.ops.object.modifier_add(type='BEVEL')
    bpy.context.object.modifiers["Bevel"].width = 0.3
    bpy.context.object.modifiers["Bevel"].segments = 8
    new_obj = bpy.context.active_object
    new_obj.name = 'Byte' + str(y) + 'x' + str(x)
    new_obj.data.materials.append(material[0])
    bpy.data.collections[choad_id].objects.link(new_obj)

def build_choad(choad_id):
    image = bpy.data.images[choad_id + '.png']
    width, height = image.size
    pixels = image.pixels[:]

    for y in range(0, height):
        for x in range(0, width):
            block_number = (y * width) + x
            alpha = pixels[(block_number * 4) + 3]
            if alpha != 0.0:
                color = []
                for color_index in range(0, 4):
                    index = (block_number * 4) + color_index
                    color.append(pixels[index])
                draw_pix(x * 2, y * 2, color, choad_id)
        #print("%(y)04d / %(height)04d" % {"y": y, "height": height})

def position_choad(choad):
    for obj in bpy.data.collections[choad].all_objects:
        obj.select_set(True)
    bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))
    bpy.ops.object.join()
    for obj in bpy.context.selected_objects:
        obj.name = "SNKRMesh"
    bpy.ops.object.select_all(action='DESELECT')


def track_animation(choad):
    bpy.data.objects["Guide"].select_set(True)
    bpy.data.objects["SNKRMesh"].select_set(True)
    bpy.ops.object.constraint_add_with_targets(type='COPY_ROTATION')
    bpy.ops.object.select_all(action='DESELECT')


def main():
    params = utils.setup_parameters()
    choad = params.choad
    render = params.render

    if choad:
        choad_id = str(choad)
        filename = choad_id

        print(choad_id + '-' + str(datetime.datetime.now().timestamp()))

        output_path = os.path.join(dirname, "../output/")
        input_image = os.path.join(dirname, "../input/" + str(choad_id) + ".png")
        # input_svg = os.path.join(dirname, "../input/" + str(choad_id) + ".svg")
        # blenderpath = output_path + "/3d/" + str(choad_id)
        blenderpath = output_path + "/3d"
        renderpath = output_path + "/render"

        Path(output_path).mkdir(parents=True, exist_ok=True)
        Path(blenderpath).mkdir(parents=True, exist_ok=True)
        Path(renderpath).mkdir(parents=True, exist_ok=True)

        build_scene(choad_id)
        build_choad(choad_id)
        position_choad(choad_id)
        track_animation(choad_id)

        utils.save_scene(blenderpath, choad_id + '-' + str(datetime.datetime.now().timestamp()))
        shutil.copy(input_image, blenderpath)
        os.remove(input_image)
        # shutil.copy(input_svg, blenderpath)

        if render:
            utils.render_scene(renderpath, filename, 1080, 1080, 100, False)

    else:
        print("No ID found")


if __name__ == "__main__":
    main()

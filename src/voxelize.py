#!/usr/bin/env python3
"""
"""

__author__ = "Matty Woodward"
__version__ = "1.0.0"
__license__ = "MIT"

import numpy as np
import magicavoxel
from PIL import Image
from struct import pack

offset = 36
model_width = 36
model_height = 36
model_depth = 18
base_adjustment = 0
frame_count = 1

def generate_color_map(colors):
  size = len(colors) + 1
  palette = np.zeros((size, 4))
  materials = []

  for index in range(1, size - 1):    
    palette[index] = np.array(colors[index][1] + (1.0,))
    mat = {
      '_type': '_metal',
      '_rough': '0.1',
      '_ior': '0.3',
      '_d': '0.05',
    }

    materials.append(mat)

  palette[size - 1] = np.array(colors[0][1] + (1.0,))
  palette = palette.astype(np.uint8)
  return (palette, materials)

def get_color(color, palette):
  size = len(palette)
  rgba = np.array([color[0],color[1],color[2], 1])
  col = 256

  for index in range(0, size):
    if (np.all(rgba == palette[index])):
      col = index

  return col

def get_coords(step, width):
  z = 0

  for x in range(0, width):
    print(x)
    if (step == x):
      return (z, step - (z * offset))
    if x % offset == 0:
      z = z + 1

def create(artwork):
    artwork_name = str(artwork)

    img = Image.open('input/{}.png'.format(artwork_name))
    image = img.load()
    width, height = img.size

    volume_list = []
    volume = np.zeros((model_width, model_depth, model_height), dtype=np.uint8)
    (palette, materials) = generate_color_map(img.convert('RGB').getcolors())

    print(width, height)

    for x in range(0, width):
        for y in range(0, height):
            if (image[x,y][3] != 0):
                (zAxis, xAxis) = get_coords(x, width)
                color = get_color(image[x,y], palette)
                yAxis = y+base_adjustment+1
                volume[-yAxis][zAxis][xAxis] = color

    volume_list.append(volume)

    output = "output/{}/{}.vox".format(artwork_name, artwork_name)
    magicavoxel.write(volume_list, output, palette, materials)
    print("{} Voxel Saved".format(artwork_name))

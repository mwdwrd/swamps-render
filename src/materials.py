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
    # color_node.inputs[19].default_value = alpha
    # print('Gloss Plastic Created: #' + hex)
import pyglet
from pyglet.window import key, mouse
import ratcave as rc
import numpy as np
from PIL import Image

import random
import math
# New imports
import argparse


# Create Window
window = pyglet.window.Window(resizable=True)
keys = key.KeyStateHandler()
window.push_handlers(pyglet.window.event.WindowEventLogger())
window.push_handlers(keys)


def get_terrain(terrain_reader, terrain_file):
    terrain = terrain_reader.get_mesh(terrain_file)
    terrain.position.xyz = 0, -4, 0
    terrain.uniforms['diffuse'] = 1,.5,.5
    return terrain

def get_tree(tree_render, tree_file):
    tree = tree_render.get_mesh(tree_file, mean_center=False)
    tree.uniforms['diffuse'] = 0.0,1.0,0.0
    return tree

def add_tree_to_terrain(terrain, vertex_id, tree_render, tree_file):
    tree = get_tree(tree_render, tree_file)
    tree.position = terrain.vertices[vertex_id]
    terrain.add_child(tree)
    return tree 

def scatter_randomly(terrain, tree_render, tree_file):
    vertex_ids = list()
    for index in range(args.tree_count):
        vertex_id = random.randint(0, len(terrain.vertices)-1)
        vertex_ids.append(vertex_id)
    return add_trees_to_terrain(terrain, vertex_ids, tree_render, tree_file)

def translate_to_range(value, from_range_min, from_range_max, to_range_min, to_range_max):
    # Figure out how 'wide' each range is
    leftSpan = from_range_max - from_range_min
    rightSpan = to_range_max - to_range_min

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - from_range_min) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return to_range_min + (valueScaled * rightSpan)

def find_vertex_pos_at(vertices, x, z):
    index = (vertices[:,0::2] == [x, z]).all(-1).argmax()
    return index

def scatter_based_on_image(terrain, tree_render, tree_file, image_path):
    size = int(math.sqrt(len(terrain.vertices)))

    img = Image.open(image_path).convert('L')
    img_resized = img.resize((size,size))

    pixels = np.array(img_resized.getdata())/255.0
    normalized_prob = (pixels/sum(pixels))

    # get indices between 0 to number of vertices with given probability ditribution
    indices = np.random.choice(len(terrain.vertices), args.tree_count, 
                                  replace=False, p=normalized_prob)

    minx = min(terrain.vertices[:,0])
    maxx = max(terrain.vertices[:,0])

    minz = min(terrain.vertices[:,2])
    maxz = max(terrain.vertices[:,2])
    vertex_ids = []

    for index in indices:
        # remap the one dim index obtained to 2D
        row = index / size
        column = index % size

        # remap this value between 0-size-1 to the range of actual x/z vertex position limits
        z_value = translate_to_range(row, 0, size-1, minz, maxz)
        x_value = translate_to_range(column, 0, size-1, minx, maxx)

        vertex_ids.append(find_vertex_pos_at(terrain.vertices, x_value, z_value))

    return add_trees_to_terrain(terrain, vertex_ids, tree_render, tree_file)


def add_trees_to_terrain(terrain, vertex_ids, tree_render, tree_file):
    trees = []
    for vertex_id in vertex_ids:
        tree = get_tree(tree_render, tree_file)
        tree.position = terrain.vertices[vertex_id]
        # Randomize scale
        tree.scale = random.random()
        # Randomize color
        red = random.randrange(0,1.0,_int=float)
        blue = random.randrange(0,1.0,_int=float)
        tree.uniforms['diffuse'] = red,1.0,blue

        terrain.add_child(tree)
        trees.append(tree)
    return trees

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tc','--tree_count', required = True, type=int, dest='tree_count', default=0, help='Number of trees to scatter')
    parser.add_argument('--image_path', required = False, type=str, dest='image_path', default=0, help='Path of the image used for probability distribution')
    parser.add_argument('--tree_path', required = False, type=str, dest='tree_path', default=0, help='Path to the tree obj')
    parser.add_argument('--terrain_path', required = False, type=str, dest='terrain_path', default=0, help='Path to the terrain obj')
    args = parser.parse_args()
    return args
args = parse_arguments()

# Put together the meshes in the scene
def build_scene():
    scene_items = []
    # Insert filename into WavefrontReader.
    terrain_file = args.terrain_path if args.terrain_path else "terrain.obj"
    terrain_reader = rc.WavefrontReader(terrain_file)
    # Get terrain mesh
    terrain = get_terrain(terrain_reader, terrain_file)
    # Get tree mesh
    tree_file = args.tree_path if args.tree_path else "tree.obj"
    # print tree_file
    tree_render = rc.WavefrontReader(tree_file)

    if args.image_path:
        trees = scatter_based_on_image(terrain, tree_render, tree_file, args.image_path)
    else:
        trees = scatter_randomly(terrain, tree_render, tree_file)

    scene_items.extend(trees)
    scene_items.append(terrain)
    return scene_items

# Create scene
scene_items = build_scene()
scene = rc.Scene(meshes=scene_items)
scene.bgColor= 138/255.0, 216/255.0, 249/255.0 

# Set fov of camera for wider view and preventing culling too soon
scene.camera.projection.fov_y = 120.

# Save camera home position, if we want to reset
cam_home = scene.camera.position.xyz    

# Allow camera translation using keyboard
def move_camera_with_keys(dt):
    camera_speed = 3
    if keys[key.LEFT]:
        scene.camera.position.x -= camera_speed * dt
    if keys[key.RIGHT]:
        scene.camera.position.x += camera_speed * dt
    if keys[key.UP]:
        scene.camera.position.y += camera_speed * dt
    if keys[key.DOWN]:
        scene.camera.position.y -= camera_speed * dt
    if keys[key.F]:
        scene.camera.position.z -= camera_speed * dt
    if keys[key.B]:
        scene.camera.position.z += camera_speed * dt
    if keys[key.HOME]:
        scene.camera.position.xyz = cam_home

# Schedule camera movement function so that it is continuously looping
pyglet.clock.schedule(move_camera_with_keys)

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    camera_speed = 1
    if mouse.LEFT & buttons:
        scene.camera.rotation.y -= camera_speed
    if mouse.RIGHT & buttons:
        scene.camera.rotation.y += camera_speed

@window.event
def on_mouse_scroll(x, y, dx, dy):
    scene.camera.rotation.x += dy   

@window.event
def on_draw():
    with rc.default_shader:
        scene.draw()

pyglet.app.run()

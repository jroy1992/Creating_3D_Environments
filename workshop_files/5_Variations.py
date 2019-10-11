import pyglet
import ratcave as rc
from pyglet.window import key, mouse
import random

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
    for index in range(random.randint(50, 150)):
        vertex_id = random.randint(0, len(terrain.vertices)-1)
        vertex_ids.append(vertex_id)
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

# Put together the meshes in the scene
def build_scene():
    scene_items = []
    # Insert filename into WavefrontReader.
    terrain_file = "terrain.obj"
    terrain_reader = rc.WavefrontReader(terrain_file)
    # Get terrain mesh
    terrain = get_terrain(terrain_reader, terrain_file)
    # Get tree mesh
    tree_file = "tree.obj"
    tree_render = rc.WavefrontReader(tree_file)

    trees = scatter_randomly(terrain, tree_render, tree_file)
    scene_items.extend(trees)
    scene_items.append(terrain)
    return scene_items

# Create scene
scene_items = build_scene()
scene = rc.Scene(meshes=scene_items)
scene.bgColor= 138/255.0, 216/255.0, 249/255.0 

# Set fov of camera for wider view and preventing culling too soon
scene.camera.projection.fov_y = 100.

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

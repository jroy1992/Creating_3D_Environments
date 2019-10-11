import pyglet
import ratcave as rc
# New imports
from pyglet.window import key, mouse

# Create Window
window = pyglet.window.Window(resizable=True)

# Add event handlers for camera movement
keys = key.KeyStateHandler()
window.push_handlers(pyglet.window.event.WindowEventLogger())
window.push_handlers(keys)

# Insert filename into WavefrontReader.
terrain_filename = "terrain.obj"
terrain_reader = rc.WavefrontReader(terrain_filename)

# Get terrain mesh
terrain = terrain_reader.get_mesh(terrain_filename)
# Set position of mesh in space
terrain.position.xyz = 0, -4, 0
# Set the colour of the mesh
terrain.uniforms['diffuse'] = 1,.5,.5

# Create Scene
scene = rc.Scene(meshes=[terrain])
scene.bgColor = 138/255.0, 216/255.0, 249/255.0 

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

# Allow camera rotation using mouse
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

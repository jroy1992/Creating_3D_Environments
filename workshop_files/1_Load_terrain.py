import pyglet
import ratcave as rc

# Create Window
window = pyglet.window.Window(resizable=True)

# Insert filename into WavefrontReader.
terrain_filename = "terrain.obj"
terrain_reader = rc.WavefrontReader(terrain_filename)

# Get terrain mesh
terrain = terrain_reader.get_mesh(terrain_filename)
# Set position of mesh in space
terrain.position.xyz = 0,-2, 0
# Set the colour of the mesh
terrain.uniforms['diffuse'] = 1,.5,.5

# Create Scene
scene = rc.Scene(meshes=[terrain])
scene.bgColor = 138/255.0, 216/255.0, 249/255.0 

@window.event
def on_draw():
    with rc.default_shader:
        scene.draw()

pyglet.app.run()

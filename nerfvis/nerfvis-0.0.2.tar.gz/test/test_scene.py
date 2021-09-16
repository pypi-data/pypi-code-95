import nerfvis
scene = nerfvis.Scene("hello world")
scene.add_axes()
scene.add_cube('Cube', translation=[1.0, 0.0, 0.0])
#  scene.add_mesh_from_file('/home/sxyu/data/example-models/teapot-low.obj')
scene.export()

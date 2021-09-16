from uberlimb import parameters
from uberlimb.renderer import Renderer
from uberlimb.video.video_recorder import VideoRecorderParams, VideoRecorder
import time
timer = time.time()
params = parameters.RendererParams()
params.model.seed = 500
params.model.variance = 5
params.input.scale = 6
params.model.activation = list(parameters.ModelActivation)[4]
params.model.out_activation = list(parameters.ModelActivation)[4]
params.model.mode = list(parameters.ModelMode)[1]
params.model.distribution = list(parameters.ModelDistribution)[2]
params.model.f_mode = list(parameters.FourierMode)[1]
# params.input.periodic_function = list(parameters.PeriodicFunctionType)[5]
params.model.architecture = list(parameters.ModelArchitecture)[1]
params.input.x_resolution = 3840
params.input.y_resolution = 2160
params.post_fx.color_map = parameters.FrameColorMap.BC_IDEA
params.post_fx.flat_colors = True
params.post_fx.dither_strength = 0
params.input.resolution_factor = 1
renderer = Renderer(params)
img = renderer.render_frame().as_pillow()
img.save('flat_idea.png')
img.show()
# recorder_params = VideoRecorderParams(filepath='video.webm',
#                                       x_resolution=params.input.x_resolution,
#                                       y_resolution=params.input.y_resolution)
# recorder = VideoRecorder(recorder_params)
# renderer.render_video(recorder)
print(time.time() - timer)
import colour
from IPython.display import Video
from datetime import datetime


class ishow_config():
    def __init__(self,
                 # file_writer_config
                 write_to_movie=True,
                 break_into_partial_movies=False,
                 save_last_frame=False,
                 save_pngs=False,
                 png_mode="RGB",
                 movie_file_extension='.mp4',
                 mirror_module_path=False,
                 output_directory=".",
                 file_name="",
                 open_file_upon_completion=False,
                 show_file_location_upon_completion=False,
                 quiet=True,
                 ##
                 write_all=False,
                 start_at_animation_number=None,
                 preview=False,
                 end_at_animation_number=None,
                 leave_progress_bars=False,
                 # class camera_config:,
                 pixel_width=1920,
                 pixel_height=1080,
                 frame_rate=30,
                 background_color="#333333",
                 # quality="default_quality",
                 # class window_config:
                 size=(960, 540),
                 skip_animations=False
                 ):
        self.default = {
            "file_writer_config": {
                "write_to_movie": write_to_movie,
                "break_into_partial_movies": break_into_partial_movies,
                "save_last_frame": save_last_frame,
                "save_pngs": save_pngs,
                "png_mode": png_mode,
                "movie_file_extension": movie_file_extension,
                "mirror_module_path": mirror_module_path,
                "output_directory": output_directory,
                "file_name": file_name,
                "open_file_upon_completion": open_file_upon_completion,
                "show_file_location_upon_completion": show_file_location_upon_completion,
                "quiet": quiet
            },
            "write_all": write_all,
            "start_at_animation_number": start_at_animation_number,
            "preview": preview,
            "end_at_animation_number": end_at_animation_number,
            "leave_progress_bars": leave_progress_bars,
            "camera_config": {
                "pixel_width": pixel_width,
                "pixel_height": pixel_height,
                "frame_rate": frame_rate,
                "background_color": colour.Color(background_color),
            },
            "window_config": {
                "size": size,
                "skip_animations": skip_animations
            },
        }

    @property
    def low(self):
        self.default["camera_config"]["pixel_width"] = 854
        self.default["camera_config"]["pixel_height"] = 480
        self.default["camera_config"]["frame_rate"] = 15
        return self.default

    @property
    def medium(self):
        self.default["camera_config"]["pixel_width"] = 1280
        self.default["camera_config"]["pixel_height"] = 720
        self.default["camera_config"]["frame_rate"] = 30
        return self.default

    @property
    def high(self):
        self.default["camera_config"]["pixel_width"] = 1920
        self.default["camera_config"]["pixel_height"] = 1080
        self.default["camera_config"]["frame_rate"] = 30
        return self.default

    @property
    def ultra_high(self):
        self.default["camera_config"]["pixel_width"] = 3840
        self.default["camera_config"]["pixel_height"] = 2160
        self.default["camera_config"]["frame_rate"] = 60
        return self.default


def ishow(scene, filename=None, config=None):
    if filename == None:
        fname = scene.__name__ + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    else:
        fname = filename
    if config == None:
        cfg = ishow_config().medium
    else:
        cfg = config
    cfg["file_writer_config"]["file_name"] = fname
    scene(**cfg).run()
    return Video("videos/" + fname + ".mp4", html_attributes="width=\"100%\" controls autoplay")


if __name__ == "__main__":
    from manimlib import *
    from imanim import ishow
    class SquaremaToCircle(Scene):
        def construct(self):
            circle = Circle()
            square = Square()
            square.flip(RIGHT)
            square.rotate(-3 * TAU / 8)
            circle.set_fill(PINK, opacity=0.5)

            self.play(ShowCreation(square))
            self.play(Transform(square, circle))
            self.play(FadeOut(square))

    ishow(SquaremaToCircle)

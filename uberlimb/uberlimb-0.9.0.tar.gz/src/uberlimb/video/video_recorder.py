import ffmpeg
import numpy as np
from pydantic import BaseModel, conint, validator


class VideoRecorderParams(BaseModel):
    filepath: str
    fps: float = 30
    bitrate: float = 20
    x_resolution: conint(gt=1, multiple_of=2)
    y_resolution: conint(gt=1, multiple_of=2)

    @validator('filepath', allow_reuse=True)
    def supported_file_format(cls, filepath: str):
        extension = filepath.split('.')[-1].lower()
        if extension not in ['mp4', 'webm']:
            raise ValueError('Only mp4 and webm formats are supported.')
        return filepath


class VideoRecorder:
    def __init__(self, params: VideoRecorderParams):
        self.params = params

    def __enter__(self):
        extension = self.params.filepath.split('.')[-1].lower()
        pipe_kwargs = {
            'mp4': {
                'c': 'libx264',
                'tune': 'animation',
                'preset': 'fast',
            },
            'webm': {
                'c': 'libvpx-vp9',
            }
        }[extension]
        self.pipe = (ffmpeg
                     .input('pipe:',
                            format='rawvideo',
                            pix_fmt='rgb24',
                            r=self.params.fps,
                            s=f'{self.params.x_resolution}x{self.params.y_resolution}')
                     .output(self.params.filepath,
                             pix_fmt='yuv420p',
                             r=self.params.fps,
                             video_bitrate=self.params.bitrate * 1000000,
                             **pipe_kwargs
                             )
                     .overwrite_output()
                     .run_async(pipe_stdin=True)
                     )
        self.entered = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pipe.stdin.close()
        self.pipe.wait()
        self.entered = False

    def write_frame(self, frame: np.ndarray):
        if not self.entered:
            raise RuntimeError('Use recorder from inside context only.')
        if frame.dtype != np.uint8:
            raise ValueError('Only np.uint8 arrays are accepted')
        if frame.shape != (expected_shape := (self.params.y_resolution,
                                              self.params.x_resolution,
                                              3)):
            raise ValueError(f'Incorrect shape: got {frame}, expected {expected_shape}')
        frame_bytes = frame.tobytes()
        self.pipe.stdin.write(frame_bytes)

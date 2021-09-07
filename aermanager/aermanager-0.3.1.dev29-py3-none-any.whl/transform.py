from torchvision import transforms
import functools
import numpy as np
import random
import torch
from typing import Tuple
from .preprocess import create_raster_from_xytp, crop_events, resize_events


class SimpleToTensor():
    def __call__(self, x: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(x.astype('float'))


class RasterizeSlice:
    """
    Generate a spike train raster from a list of events sliced by time and id.
    """
    def __init__(self, dt, bins_x, bins_y):
        self.dt = dt
        self.bins_x = bins_x
        self.bins_y = bins_y

    def __call__(self, xytp: np.ndarray) -> np.ndarray:
        return create_raster_from_xytp(xytp, self.dt, self.bins_y, self.bins_x)


class CollapseChannels:
    """
    Collapse the polarity channels.
    """
    def __call__(self, frame: torch.Tensor):
        return frame.sum(0, keepdim=True)


class CropEvents:
    """
    Transform to center crop events from a xytp, based on an input size and a crop size.
    See `preprocess.crop_events` for more details
    Args:
        input_shape (Tuple): A tuple (height, width)
        crop_size (Tuple(Tuple)): A tuple of the borders to crop ((left, right), (top, bottom))
    """
    def __init__(self, input_size, crop_size):
        self.input_size = input_size
        self.crop_size = crop_size

    def __call__(self, xytp: np.ndarray) -> np.ndarray:
        return crop_events(xytp, self.input_size, self.crop_size)


class ResizeEvents:
    """
    Transform to centerize spikes on a larger pixel array
    Args:
        shape (Tuple): Shape of the output frame of xytp (height, width)
    """
    def __init__(self, output_size: Tuple):
        self.output_size = output_size

    def __call__(self, xytp):
        return resize_events(xytp, self.output_size)


def apply_by_channel(transform):
    """
    Takes a transform function and turns it into another transform, that will be applied independently to each channel.
    This is useful when using torchvision transforms, which interpret channels as RGB, and do PIL weirdness with them.
    Additionally, ToPILImage will automatically be applied to the image.
    This has been checked with uint8 and float32 inputs and preserves these types and their ranges.
    This function can be used as a decorator for your function.


    :param transform: A transformation function.
    :return: The same transformation function, modified as described.
    """
    # TODO: Add deprication warning

    to_pil_image = transforms.ToPILImage()

    def channel_transform(image):
        new_image = []
        # record the random number generator state
        seed = np.random.randint(2147483647)
        for i, channel in enumerate(image):
            random.seed(seed)
            torch.manual_seed(seed)

            channel = to_pil_image(channel)
            channel = transform(channel)
            new_image.append(np.asarray(channel))
        return np.asarray(new_image)

    @functools.wraps(transform)
    def wrapper(image):
        if image.ndim == 3:
            return channel_transform(image)

        elif image.ndim == 4:
            shape = image.shape
            new_image = channel_transform(image.reshape((-1, *shape[-2:])))
            return new_image.reshape((*shape[:2], *new_image.shape[-2:]))

        else:
            raise ValueError("Input must be a 3d image (channels, x, y) or a 4d video (time, channels, x, y)")

    return wrapper


class AddShotNoiseToFrame:
    """
    Designed to be used together with torchvision.tranform.Compose

    This method introduce addtive poission noise to frames, this simulates the shot-noise which indicated by
    the noise-frequency per pixel. Each pixel in the limited time window at each timestep
    will have a probability to generate a spike, where avereaving frequency in the time_window is specified
    frequency

    :param: Hz: Average shot-noise frequency per pixel
            time_window: time window in (ms)
            dt{defaut=1}: time resolution in (ms)
                          do not need to be specified when ndim ==4 (timestep, channel, y, x)
            n_dim: the dimension of input(3/4), has to be indicated to produce correct frequency of shot-noise
    :return image object which is consistent with torchvision.transform manaer

    """
    def __init__(self, Hz, time_window, dt: int = 1, n_dim: int =3):

        self.Hz = Hz
        self.dt = dt
        self.time_window = time_window
        self.n_dim = n_dim

    def __call__(self, x: np.ndarray):
        if self.n_dim == 3:
            # This is a frame
            # this will apply to both on/off channel
            noise = np.random.rand(int(self.time_window/self.dt), *x.shape) <= self.Hz / (self.dt * 1000)
            noise = noise.sum(0)
            x = x + noise
        elif self.n_dim == 4:
            # Spike raster with time dimension
            noise = np.random.rand(*x.shape) <= self.Hz / (self.dt * 1000)
            x = x + 1 * noise

        else:
            raise Exception(f"dimension error:{x.ndim}")

        return x
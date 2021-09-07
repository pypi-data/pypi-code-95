import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation


def _display_frame(frame, label=None, ax=None):
    assert frame.ndim == 3, f"Image must have 3 dimensions, found {frame.ndim}"
    assert len(frame) == 2, f"Image must have 2 channels, found {len(frame)}"

    if ax is None:
        ax = plt.gca()
    if label is not None:
        ax.set_title("Label: " + str(label))

    diff = frame[0] - frame[1]
    maxdiff = np.abs(diff).max()
    ax.imshow(diff, cmap=plt.cm.coolwarm, vmin=-maxdiff, vmax=maxdiff)
    ax.set_axis_off()


def display_frames(frames, labels=None, ncols=4):
    """
    Displays all frames in a grid
    """
    if frames.ndim == 3:
        return _display_frame(frames, label=labels)

    assert frames.ndim == 4, "Expected array of 3d images"
    nframes = len(frames)
    nrows = int(np.ceil(nframes / ncols))

    for i in range(nframes):
        label = labels[i] if labels is not None else None
        plt.subplot(nrows, ncols, i + 1)
        _display_frame(frames[i], label)

    plt.show()


def events_animation(xytp: np.ndarray, timescale, framerate=24, repeat=False, show=False):
    """
    :param xytp:  events np arrary, with strict ["x"], ["y"], ["t"], ["p"] to call correspond event information
                  p should be either 1/0 or True/False to represent ON/OF polarity
    :param timescale: the timescale of recording events (ms)
    :param framerate: framerate of animation
    :param repeat(boolean):  if repeat
    :param show(boolean):  if show the animation

    :return: animation object
    """

    fig = plt.figure()

    xdim, ydim = xytp["x"].max() + 1, xytp["y"].max() + 1
    interval = 1e3 / framerate

    minFrame = int(np.floor(xytp["t"].min()) / timescale / interval)
    maxFrame = int(np.ceil(xytp["t"].max()) / timescale / interval)
    Image = plt.imshow(np.zeros((ydim, xdim, 3)))
    frames = np.zeros((maxFrame - minFrame, ydim, xdim, 3))

    for i in range(len(frames)):
        tStart = (i + minFrame) * interval
        tEnd = (i + minFrame + 1) * interval
        timeMask = (xytp["t"] / timescale >= tStart) & (xytp["t"] / timescale < tEnd)
        rInd = timeMask & (xytp["p"].astype("uint8") == 1)
        gInd = timeMask & (xytp["p"].astype("uint8") == 0)

        frames[i, xytp["y"][rInd], xytp["x"][rInd], 0] = 1
        frames[i, xytp["y"][gInd], xytp["x"][gInd], 1] = 1

    def animate(inputFrame):
        Image.set_data(inputFrame)
        return Image

    anim = animation.FuncAnimation(fig, animate, frames=frames, interval=interval, repeat=repeat)
    if show:
        plt.show()
    return anim

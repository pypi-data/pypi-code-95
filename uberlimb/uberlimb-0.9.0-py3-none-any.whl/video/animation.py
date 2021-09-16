import math

import numpy as np


def bernoulli_animation(alpha: float, beta: float, num_frames: int):
    video_length = 60
    t = np.linspace(-0.5 * np.pi, 0.5 * np.pi, num_frames)
    a = 2 * video_length / 60
    x = a * np.cos(t) / (1 + np.sin(t) ** 2)
    y = a * np.sin(t) * np.cos(t) / (1 + np.sin(t) ** 2)
    x_rot = x * np.cos(np.pi / 4) - y * np.sin(np.pi / 4)
    y_rot = x * np.sin(np.pi / 4) + y * np.cos(np.pi / 4)
    if alpha < 0:
        x_rot *= -1
    if beta < 0:
        y_rot *= -1
    x_rot += alpha
    y_rot += beta
    alpha_beta = list(zip(x_rot, y_rot))
    return alpha_beta


def animate_alpha_beta(alpha: float, beta: float, num_frames: int):
    radius = (alpha ** 2 + beta ** 2) ** 0.5
    angle = math.atan2(beta, alpha)
    alphas = [radius * math.cos(angle + i * math.pi / num_frames * 2) for i in
              range(num_frames)]
    betas = [radius * math.sin(angle + i * math.pi / num_frames * 2) for i in
             range(num_frames)]
    alpha_beta = list(zip(alphas, betas))
    return alpha_beta

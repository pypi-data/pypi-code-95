import pygame


def scale_image(image: pygame.Surface, factor: float):
    size = image.get_size()
    return pygame.transform.scale(image, (int(size[0] * factor), int(size[1] * factor)))

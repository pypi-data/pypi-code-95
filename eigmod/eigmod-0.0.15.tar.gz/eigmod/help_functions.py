import pygame

pygame.init()

def get_font_size(font_name, given_height):
    test_size = 100
    test_font = pygame.font.SysFont(font_name, test_size)
    t_test_font = test_font.render("test", True, (255, 255, 255))
    font_height = t_test_font.get_height()
    height_per_size = font_height/test_size
    font_size = int(round(given_height / height_per_size, 0))

    return font_size

def get_croped_rect(bigrect, smallrect):

    croped_rect = pygame.Rect(0,0,0,0)

    if not bigrect.contains(smallrect):
        r = smallrect.clip(bigrect)
        croped_rect.width = r.width
        croped_rect.height = r.height
        croped_rect.x = bigrect.x - \
            smallrect.x if bigrect.x - smallrect.x > 0 else 0
        croped_rect.y = bigrect.y - \
            smallrect.y if bigrect.y - smallrect.y > 0 else 0
    else:
        croped_rect = pygame.Rect(0, 0, smallrect.width,
                                           smallrect.height)

    return croped_rect

def clip(value, vmin, vmax):

    if vmin >= vmax:
        raise ValueError

    if value > vmax:
        value = vmax
    if value < vmin:
        value = vmin

    return value

def iround(v):
    return int(round(v, 1))

def center_rect(big_rect, small_rect):
    
    x = big_rect.x + big_rect.width/2 - small_rect.width/2
    y = big_rect.y + big_rect.height/2 - small_rect.height/2

    return x, y

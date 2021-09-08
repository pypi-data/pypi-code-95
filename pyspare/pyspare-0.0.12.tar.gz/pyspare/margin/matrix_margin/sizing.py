from veho.matrix import size


def sizing(matrix, top, bottom, left, right, height=None, width=None):
    if not height or not width: (height, width) = size(matrix)
    if not height or not width: top, bottom = 0, 0
    if (not top and not bottom) or (top + bottom >= height): top, bottom = height, 0
    if (not left and not right) or (left + right >= width): left, right = width, 0
    return top, bottom, left, right, height, width

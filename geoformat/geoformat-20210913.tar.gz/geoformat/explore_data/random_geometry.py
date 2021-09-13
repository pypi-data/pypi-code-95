import random

def random_point(bbox, nb_round=2):
    """
    Renvoie un point au hasard compris dans une bbox

    Entree :
        bbox : boundary box dans laquelle on veut voir le point

    Sortie :
        Retourne un point au hasard dans la bbox
    """

    (min_x, min_y, max_x, max_y) = bbox

    x = round(min_x + random.random() * (max_x - min_x), nb_round)
    y = round(min_y + random.random() * (max_y - min_y), nb_round)

    return x, y


def random_segment(bbox, nb_round=2):
    """

    :param bbox:
    :param nbRound:
    :return:
    """
    (min_x, min_y, max_x, max_y) = bbox

    xBegin = round(min_x + random.random() * (max_x - min_x), nb_round)
    yBegin = round(min_y + random.random() * (max_y - min_y), nb_round)
    xEnd = round(min_x + random.random() * (max_x - min_x), nb_round)
    yEnd = round(min_y + random.random() * (max_y - min_y), nb_round)

    return (xBegin, yBegin), (xEnd, yEnd)


def random_bbox(bbox, nb_round=2):
    """
    Return random bbox

        Input:
            bbox

        Output:
            new_bbox (bbox)
    """
    x_list, y_list = [0, 0], [0, 0]
    for i in range(2):
        x_list[i] = round(bbox[0] + random.random() * (bbox[2] - bbox[0]), nb_round)
        y_list[i] = round(bbox[1] + random.random() * (bbox[3] - bbox[1]), nb_round)

    new_bbox = (min(x_list), min(y_list), max(x_list), max(y_list))

    return new_bbox


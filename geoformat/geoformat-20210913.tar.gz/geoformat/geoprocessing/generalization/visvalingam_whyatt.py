from geoformat.geoprocessing.measure.area import triangle_area

# - récupère une liste de coordonnées(points) en mètres.
# - récupère une tolérance (superficie minimale à afficher).

# - calcule l'aire du triangle en partant du 1er point (points 1,2,3):
#   (hauteur X base) / 2.
# - change le point de départ (+1) et calcul l'aire du nouveau triangle.
# - stocke en mémoire tous les aires des triangles.
# - s'arrête de calculer les aires dès qu'il n'y a que deux points de disponible.

# - cherche la plus petite aire, supprime le deuxième point du triangle et le nombre de points restant.
# - même chose jusqu'à ce qu'il n'y ait plus rien à simplifier.


def _recompute_idx_point_with_low_area(_coordinate_list, _idx, _coordinates_idx_with_low_area, _tolerance):
    """
    The aim of this function is to recompute, after a point deletion, triangular area for points after and before
    deleted point if it's possible.
    If area if lower than tolerance we add idx point in coordinates_idx_with_low_area to make deletion.


    :param _coordinate_list:
    :param _idx:
    :param _coordinates_idx_with_low_area:
    :param _tolerance:
    :return: updated coordinates_idx_with_low_area
    """

    # TODO rendre possible l'ordre de suppression des points par poids (taille de l'aire) ?
    # TODO usage des sets VS listes (perf-test)

    # if there are enough coordinates to compute triangle after
    # AND we have not yet decide to delete point before
    if _idx >= 2:
        triangle_before_area = triangle_area(vertex_a=_coordinate_list[_idx - 2], vertex_b=_coordinate_list[_idx - 1],
                                             vertex_c=_coordinate_list[_idx])
        if _idx - 1 not in _coordinates_idx_with_low_area:
            if triangle_before_area < _tolerance:
                _coordinates_idx_with_low_area = _coordinates_idx_with_low_area + [_idx - 1]
        # if point immediately before is in _coordinates_idx_with_low_area we have to recompute new area a this point
        # (because area have change) if new area > _tolerance this before point must be keep in coordinate list
        else:
            if triangle_before_area > _tolerance:
                del _coordinates_idx_with_low_area[_coordinates_idx_with_low_area.index(_idx - 1)]

    # if there are enough coordinates to compute triangle after
    if len(_coordinate_list) - 1 >= _idx + 1:
        triangle_after_area = triangle_area(vertex_a=_coordinate_list[_idx - 1], vertex_b=_coordinate_list[_idx],
                                            vertex_c=_coordinate_list[_idx + 1])
        if triangle_after_area < _tolerance:
            _coordinates_idx_with_low_area = _coordinates_idx_with_low_area + [_idx]

    return _coordinates_idx_with_low_area


def visvalingam_whyatt(coordinate_list, tolerance):
    """
    This function is a generalizatio algorithm.
    It's take a coordinate's list and a tolerance value and return a simplified coordinate's list.

    documentation :
        https://en.wikipedia.org/wiki/Visvalingam%E2%80%93Whyatt_algorithm
        https://bost.ocks.org/mike/simplify/


    :param coordinate_list: coordinate's list
    :param tolerance: minimum area in coordinates units
    :return: simplified coordinates
    """
    # if coordinates_list is not empty and have more than 2 coordinates
    if len(coordinate_list) > 2:

        coordinates_idx_with_low_area = []
        nb_coordinates = len(coordinate_list)
        for i_point, point in enumerate(coordinate_list):
            # get points to compute triangular area
            if i_point == 0:
                continue
            elif i_point == nb_coordinates - 1:
                break
            else:
                point_a = coordinate_list[i_point - 1]

            point_b = point
            point_c = coordinate_list[i_point + 1]
            # area calculation
            area = triangle_area(point_a, point_b, point_c)
            if area < tolerance:
                coordinates_idx_with_low_area.append(i_point)

        # if there is coordinates to delete
        if coordinates_idx_with_low_area:
            # we loop on list until there is coordinates inside
            while coordinates_idx_with_low_area:
                # get idx to coordinates and delete it from while coordinates_idx_with_low_area
                idx = coordinates_idx_with_low_area[-1]
                del coordinates_idx_with_low_area[-1]
                # delete low area coordinates with idx
                del coordinate_list[idx]

                # now we have to recalculated area for triangle before and after deleting point (if it's possible)
                coordinates_idx_with_low_area = _recompute_idx_point_with_low_area(
                    _coordinate_list=coordinate_list,
                    _idx=idx,
                    _coordinates_idx_with_low_area=coordinates_idx_with_low_area,
                    _tolerance=tolerance
                )

    return coordinate_list

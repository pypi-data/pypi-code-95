import numpy as np


def process_tour_info(tours, coords):
    tour_length_dict = dict()
    total_tour_length = 0.0
    n_inactive = 0

    for m, tour in tours.items():
        src, dst = tour[:-1], tour[1:]
        tl = np.sqrt(((coords[src] - coords[dst]) ** 2).sum(axis=1)).sum()
        tour_length_dict[m] = tl
        if tl <= 0.0:
            n_inactive += 1
        total_tour_length += tl

    max_tour_len = max(tour_length_dict.values())
    min_tour_len = min(tour_length_dict.values())
    amplitude = max_tour_len - min_tour_len
    return tour_length_dict, amplitude, total_tour_length, n_inactive

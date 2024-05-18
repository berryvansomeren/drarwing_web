from finch.primitive_types import Point, Image

import numpy as np


def sample_weighted_position_from_image(diff_image: Image) -> Point:
    flat_weights = diff_image.ravel()
    flat_probabilities = flat_weights / np.sum(flat_weights)
    random_flat_index = np.random.choice(flat_weights.size, p=flat_probabilities)
    position = np.unravel_index(random_flat_index, diff_image.shape)
    return Point(int(position[1]), int(position[0]))

import numpy as np

from finch.absolute_difference_image import get_absolute_difference_image, get_relative_difference_image
from finch.primitive_types import Image, FitnessScore
from finch.specimen import Specimen


def _get_fitness_from_absolute_difference_image( diff_image : Image ) -> FitnessScore:
    image_score = float( np.sum( diff_image ) )
    n_elements = np.prod( diff_image.shape )
    max_potential_diff_score = n_elements * 255
    normalized_diff_score = image_score / max_potential_diff_score
    return normalized_diff_score


def get_fitness( specimen: Specimen, target_image : Image, use_relative_difference ) -> FitnessScore :
    """
    Note that throughout this project it is assumed that lower fitness scores are better.
    Scores are commonly a percentage, measuring equality between result and target
    """
    if use_relative_difference:
        difference_image = get_relative_difference_image( specimen.cached_image, target_image )
    else:
        difference_image = get_absolute_difference_image( specimen.cached_image, target_image )
    specimen.diff_image = difference_image
    fitness = _get_fitness_from_absolute_difference_image(difference_image)
    return fitness
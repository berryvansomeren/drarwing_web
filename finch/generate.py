import cv2
import logging
import math
import numpy as np

from finch.brush import (
    Brush,
    random_brush_texture_index,
    draw_brush_on_image,
    get_brush_size_for_fitness,
)
from finch.difference_image import DifferenceMethod
from finch.fitness import get_fitness
from finch.image_gradient import ImageGradient
from finch.image_utils import get_color_from_image, scale_image
from finch.primitive_types import Image, FitnessScore
from finch.sample_weighted_position_from_image import sample_weighted_position_from_image
from finch.specimen import Specimen

logger = logging.getLogger(__name__)

DECIMALS = 3
SCORE_MULTIPLIER = 10 ** DECIMALS

DIFF_IMAGE_FACTOR = 4
N_ITERATIONS_PATIENCE : int = 100
TERMINATION_SCORE: int = 3500


def _get_blank_image_like( example_image: Image ) -> Image:
    blank_image = np.zeros_like( example_image )
    blank_image.fill( 255 )
    return blank_image


def get_initial_specimen( target_image : Image ) -> Specimen:
    blank_image = _get_blank_image_like( target_image )
    specimen = Specimen(cached_image = blank_image )
    return specimen


def iterate_image(
    specimen: Specimen,
    fitness: FitnessScore,
    target_image: Image,
    target_gradient: ImageGradient,
    store_brushes: bool = True,
    diff_method: DifferenceMethod = DifferenceMethod.ABSOLUTE,
) -> tuple[Specimen, FitnessScore, int]:
    new_specimen = specimen.copy()
    _mutate_specimen_inplace(
        specimen = new_specimen,
        fitness = fitness,
        target_image = target_image,
        target_gradient = target_gradient,
        store_brushes=store_brushes,
    )
    new_fitness = get_fitness(specimen=new_specimen, target_image=target_image, diff_method=diff_method)
    new_rounded_score = round(new_fitness * 100 * SCORE_MULTIPLIER)
    return new_specimen, new_fitness, new_rounded_score


def _mutate_specimen_inplace(
        specimen : Specimen,
        fitness : FitnessScore,
        target_image : Image,
        target_gradient : ImageGradient,
        store_brushes: bool = True,
) -> None:
    diff_image_small = scale_image(specimen.diff_image, 1 / DIFF_IMAGE_FACTOR)
    position = sample_weighted_position_from_image( diff_image = diff_image_small )
    position.mult(DIFF_IMAGE_FACTOR)
    color = get_color_from_image( image = target_image, position = position )
    texture_index = random_brush_texture_index()
    angle = math.degrees( target_gradient.get_direction( position ) )
    brush_size = get_brush_size_for_fitness(
        fitness = fitness,
        image_height = target_image.shape[0],
        image_width = target_image.shape[1]
    )
    new_brush = Brush(
        color = color,
        position = position,
        texture_index = texture_index,
        angle = angle,
        size = brush_size,
    )
    draw_brush_on_image( brush = new_brush, image = specimen.cached_image )
    if store_brushes:
        specimen.brushes.append( new_brush )


def is_drawing_finished(n_iterations_with_same_score: int, score: int) -> bool:
    # If ran out of patience, write the final result, and break
    ran_out_of_patience = n_iterations_with_same_score == N_ITERATIONS_PATIENCE
    reached_termination_score = score <= TERMINATION_SCORE
    if ( ran_out_of_patience or reached_termination_score ):
        if ran_out_of_patience:
            logger.info( 'Ran out of patience.' )
        else:
            logger.info( 'Reached termination score.' )
        return True
    return False

import copy
import logging
import os

from datetime import datetime
from enum import Enum, auto
import math
from pathlib import Path
import pickle

import random
import cv2
import numpy as np

from finch.brush import (
    Brush,
    BrushSet,
    preload_brush_textures_for_brush_set,
    random_brush_texture_index,
    draw_brush_on_image,
    get_brush_size_for_fitness,
    str_to_brush_set
)
from finch.generate import get_initial_specimen, iterate_image, is_drawing_finished
from finch.image_utils import get_color_from_image
from finch.fitness import get_fitness
from finch.gif import make_gif
from finch.image_gradient import ImageGradient
from finch.primitive_types import Image, FitnessScore
from finch.sample_weighted_position_from_image import sample_weighted_position_from_image
from finch.redraw import redraw_painting_at_4k
from finch.scale import normalize_image_size
from finch.specimen import Specimen


FIXED_RANDOM_SEED = 1337
DECIMALS = 3
SCORE_MULTIPLIER = 10 ** DECIMALS

N_ITERATIONS_PATIENCE : int = 100
SCORE_INTERVAL: int = 0.5 * SCORE_MULTIPLIER
TERMINATION_SCORE: int = 3500

ROOT_DIR                        = Path( __file__ ).parent.parent
DEFAULT_OUTPUT_DIRECTORY_PATH   = ROOT_DIR / '_results'
DEFAULT_INPUT_IMAGE_PATH        = ROOT_DIR / '_input_images'


logger = logging.getLogger(__name__)


WRITE_OUTPUT = False
WRITE_PICKLE = False
MAKE_GIF = False
LOG_SCORES = True


class Config(Enum):
    DEBUG = auto()
    PROD = auto()


def set_global_config( config : Config ) -> None:
    global WRITE_OUTPUT
    global WRITE_PICKLE
    global MAKE_GIF
    global LOG_SCORES
    if config == Config.DEBUG:
        WRITE_OUTPUT = True
        WRITE_PICKLE = False
        MAKE_GIF = True
        LOG_SCORES = True
    else:
        WRITE_OUTPUT = False
        WRITE_PICKLE = False
        MAKE_GIF = True
        LOG_SCORES = False


def mutate_specimen_inplace(
        specimen : Specimen,
        fitness : FitnessScore,
        target_image : Image,
        target_gradient : ImageGradient,
        diff_image : Image
) -> None:
    position = sample_weighted_position_from_image( diff_image = diff_image )
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
    specimen.brushes.append( new_brush )


def write_results(report_string : str, image : Image, specimen : Specimen) -> None:
    if not WRITE_OUTPUT:
        return
    cv2.imwrite( f'{DEFAULT_OUTPUT_DIRECTORY_PATH}/{report_string}.png', image )
    # store pickled specimen if desired
    if WRITE_PICKLE:
        pickle_file_path = f'{DEFAULT_OUTPUT_DIRECTORY_PATH}/{report_string}.pickle'
        with open( pickle_file_path, 'wb' ) as pickle_file :
            pickle.dump( specimen.__dict__, pickle_file )


def run_finch_generator(
    target_image    : Image,
    brush_set       : BrushSet,
) -> Image | tuple[Image, bytes]:
    preload_brush_textures_for_brush_set( brush_set = brush_set )
    target_gradient = ImageGradient( image = target_image )

    last_rounded_score = 100 * SCORE_MULTIPLIER
    last_written_score = last_rounded_score
    n_iterations_with_same_score = 0
    last_update_time = datetime.now()

    logger.info('Running visual genetic algorithm')
    start_time = datetime.now()

    # use a seed to make things reproducible
    random.seed( FIXED_RANDOM_SEED )
    np.random.seed( FIXED_RANDOM_SEED )

    generation_index = 0

    specimen = get_initial_specimen( target_image = target_image )
    fitness = get_fitness( specimen = specimen, target_image = target_image )
    rounded_score = 9999999

    result_frames = []
    if MAKE_GIF:
        result_frames.append( copy.deepcopy( specimen.cached_image ) )

    while True:
        generation_index += 1

        new_specimen, new_fitness, new_rounded_score = iterate_image(
            specimen,
            fitness,
            target_image,
            target_gradient,
        )

        # Only keep the new version if it is an improvement
        if new_rounded_score >= rounded_score:
            n_iterations_with_same_score += 1
        else:
            n_iterations_with_same_score = 0
            fitness = new_fitness
            rounded_score = new_rounded_score
            specimen = new_specimen

        current_update_time = datetime.now()
        update_time_microseconds = ( current_update_time - last_update_time ).microseconds
        last_update_time = current_update_time

        report_string = f'gen_{generation_index:06d}__dt_{update_time_microseconds}_ms__score_{rounded_score}'

        if LOG_SCORES:
            logger.info( report_string )

        # We only write images if they show enough improvement compared to the last written one
        if last_written_score - rounded_score >= SCORE_INTERVAL :
            write_results( report_string, specimen.cached_image, specimen )
            last_written_score = rounded_score
            if MAKE_GIF:
                result_frames.append( copy.deepcopy( specimen.cached_image ) )

        # If ran out of patience, write the final result, and break
        if ( is_drawing_finished(n_iterations_with_same_score, rounded_score) ):
            write_results( report_string, specimen.cached_image, specimen)
            break

    # make sure to include the last frame in the GIF,
    # even though it did not meet the score_interval
    if MAKE_GIF :
        result_frames.append( copy.deepcopy( specimen.cached_image ) )

    end_time = datetime.now()
    convergence_time = end_time - start_time
    logger.info( f'Converged in {convergence_time.seconds} seconds.' )

    logger.info( 'Creating 4K version' )
    result_4k = redraw_painting_at_4k( specimen = specimen )

    if WRITE_OUTPUT:
        output_path_4k = DEFAULT_OUTPUT_DIRECTORY_PATH / '___final_result_4k.png'
        cv2.imwrite( output_path_4k, result_4k )
        logger.info( f'Wrote 4k result to {output_path_4k}' )

    if MAKE_GIF:
        output_path_gif = DEFAULT_OUTPUT_DIRECTORY_PATH / '___final_result_gif.gif'
        gif_buffer = make_gif(result_frames)
        logger.info( f'Wrote GIF result to {output_path_gif}' )

        if WRITE_OUTPUT:
            with open( output_path_gif, 'wb' ) as f :
                f.write( gif_buffer )

        logger.info( f'DONE!' )
        return result_4k, gif_buffer

    logger.info( f'DONE!' )
    return result_4k



def run_finch( image : np.ndarray, brush_set_name : str ) -> np.ndarray:
    normalized_image = normalize_image_size( image )

    brush_set = str_to_brush_set( brush_set_name )
    result = run_finch_generator(
        target_image = normalized_image,
        brush_set = brush_set
    )
    return result
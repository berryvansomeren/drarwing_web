import logging

from datetime import datetime
import time
from enum import Enum, auto
import math
from pathlib import Path
import pickle
from os import listdir
from os.path import isfile, join

import random
import cv2
import numpy as np

from finch.absolute_difference_image import get_absolute_difference_image
from finch.brush import (
    Brush,
    BrushSet,
    preload_brush_textures_for_brush_set,
    random_brush_texture_index,
    draw_brush_on_image,
    get_brush_size_for_fitness,
    str_to_brush_set
)
from finch.color_from_image import get_color_from_image
from finch.fitness import get_fitness
from finch.image_gradient import ImageGradient
from finch.primitive_types import Image, FitnessScore, Point
from finch.sample_weighted_position_from_image import sample_weighted_position_from_image
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

WINDOW_NAME = "drarwing_continuous"
WINDOW_DIFF = "drarwing_continuous_diff"
MAXIMUM_TIME_PER_IMAGE_SECONDS = 5 * 60
MINIMUM_FRAME_TIME_S = 0.01


logger = logging.getLogger(__name__)


WRITE_OUTPUT = False
WRITE_PICKLE = False
MAKE_GIF = False

DEBUG = False
FULLSCREEN = True
SHOW_DIFF = False

class Config(Enum):
    DEBUG = auto()
    PROD = auto()


def set_global_config( config : Config ) -> None:
    global WRITE_OUTPUT
    global WRITE_PICKLE
    global MAKE_GIF
    if config == Config.DEBUG:
        WRITE_OUTPUT = True
        WRITE_PICKLE = False
        MAKE_GIF = True
    else:
        WRITE_OUTPUT = False
        WRITE_PICKLE = False
        MAKE_GIF = True


def get_blank_image_like( example_image: Image ) -> Image:
    blank_image = np.zeros_like( example_image )
    blank_image.fill( 255 )
    return blank_image


def get_initial_specimen( target_image : Image ) -> Specimen:
    blank_image = get_blank_image_like( target_image )
    specimen = Specimen(cached_image = blank_image )
    return specimen


def mutate_specimen_inplace(
        specimen : Specimen,
        fitness : FitnessScore,
        target_image : Image,
        target_gradient : ImageGradient,
        store_brushes: bool = True,
) -> None:
    DIFF_IMAGE_FACTOR = 4
    diff_image_small = cv2.resize(
        specimen.diff_image,
        (int(specimen.diff_image.shape[1] / DIFF_IMAGE_FACTOR), int(specimen.diff_image.shape[0] / DIFF_IMAGE_FACTOR))
    )
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


def write_results(report_string : str, image : Image, specimen : Specimen) -> None:
    if not WRITE_OUTPUT:
        return
    cv2.imwrite( f'{DEFAULT_OUTPUT_DIRECTORY_PATH}/{report_string}.png', image )
    # store pickled specimen if desired
    if WRITE_PICKLE:
        pickle_file_path = f'{DEFAULT_OUTPUT_DIRECTORY_PATH}/{report_string}.pickle'
        with open( pickle_file_path, 'wb' ) as pickle_file :
            pickle.dump( specimen.__dict__, pickle_file )


def prep_image(img_path: str) -> Image:
    image = cv2.imread( img_path )
    # image = cv2.blur(image,(5,5))
    if FULLSCREEN:
        return normalize_image_size( image, max_dimension=3440 )
    else:
        return normalize_image_size( image, max_dimension=720 )


def window_exists(window_name):
    try:
        return cv2.getWindowProperty(window_name, 0) >= 0
    except:
        return False


def _get_random_image_path(image_folder: str, previous: str | None) -> str:
    img_paths = [join(image_folder, f) for f in listdir(image_folder) if isfile(join(image_folder, f))]
    img_path = previous
    while img_path == previous:
        img_path = random.choice(img_paths)
    return img_path


def run_finch_generator(
    image_folder     : str,
    brush_sets       : list[BrushSet],
) -> Image | tuple[Image, bytes]:

    img_path: str | None = None

    n_iterations_with_same_score = 0
    last_update_time = datetime.now()

    # use a seed to make things reproducible
    # random.seed( FIXED_RANDOM_SEED )
    # np.random.seed( FIXED_RANDOM_SEED )

    initial = True
    stop = False

    if FULLSCREEN:
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.namedWindow(WINDOW_NAME)

    if SHOW_DIFF:
        cv2.namedWindow(WINDOW_DIFF)

    while not stop:

        img_path = _get_random_image_path(image_folder, img_path)
        brush_set = random.choice(brush_sets)
        preload_brush_textures_for_brush_set( brush_set = brush_set )

        logger.info(f"Drawing image {img_path}")
        target_image = prep_image(img_path)
        target_gradient = ImageGradient( image = target_image )
        if initial:
            specimen = get_initial_specimen( target_image = target_image )
            initial = False
        fitness = get_fitness( specimen = specimen, target_image = target_image )
        rounded_score = 9999999
        generation_index = 0

        image_start_time = time.time()

        while time.time() - image_start_time < MAXIMUM_TIME_PER_IMAGE_SECONDS:
            frame_start_time = time.time()
            generation_index += 1

            # Mutate a copy of the specimen
            new_specimen = specimen.copy()
            mutate_specimen_inplace(
                specimen = new_specimen,
                fitness = fitness,
                target_image = target_image,
                target_gradient = target_gradient,
                store_brushes=False,
            )
            new_fitness = get_fitness( specimen = new_specimen, target_image = target_image )
            new_rounded_score = round( new_fitness * 100 * SCORE_MULTIPLIER )

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

            logger.debug( report_string )

            if not window_exists(WINDOW_NAME):
                stop = True
                break
            if DEBUG:
                img = specimen.cached_image.copy()
                img = cv2.putText(
                    img,
                    f"{img_path}-{brush_set.name} {update_time_microseconds} ms, {rounded_score} score",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA
                )
                cv2.imshow(WINDOW_NAME, img)
            else:
                cv2.imshow(WINDOW_NAME, specimen.cached_image)

            if SHOW_DIFF:
                cv2.imshow(WINDOW_DIFF, specimen.diff_image)

            key = cv2.waitKey(1)
            if key > -1:
                stop = True
                break

            # If ran out of patience, write the final result, and break
            ran_out_of_patience = n_iterations_with_same_score == N_ITERATIONS_PATIENCE
            reached_termination_score = rounded_score <= TERMINATION_SCORE
            if ( ran_out_of_patience or reached_termination_score ):
                if ran_out_of_patience:
                    logger.info( 'Ran out of patience.' )
                else:
                    logger.info( 'Reached termination score.' )
                break

            frame_time = time.time() - frame_start_time
            if frame_time < MINIMUM_FRAME_TIME_S:
                time.sleep(MINIMUM_FRAME_TIME_S - frame_time)


def run_finch( image : np.ndarray, brush_set_name : str ) -> np.ndarray:
    normalized_image = normalize_image_size( image )

    brush_set = str_to_brush_set( brush_set_name )
    result = run_finch_generator(
        target_image = normalized_image,
        brush_set = brush_set
    )
    return result

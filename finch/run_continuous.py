import logging

from datetime import datetime
import time
from os import listdir
from os.path import isfile, join
from threading import Thread

import random
import cv2

from finch.brush import (
    BrushSet,
    preload_brush_textures_for_brush_set,
)
from finch.fitness import get_fitness
from finch.generate import get_initial_specimen, iterate_image, is_drawing_finished
from finch.image_gradient import ImageGradient
from finch.primitive_types import Image
from finch.render import render_thread
from finch.scale import normalize_image_size
from finch.shared_state import State

logger = logging.getLogger(__name__)

MAXIMUM_TIME_PER_IMAGE_SECONDS = 5 * 60
MINIMUM_STEP_TIME_SECONDS = 0.00001

DEBUG = True
FULLSCREEN = False
SHOW_DIFF = False


def _prep_image(img_path: str) -> tuple[Image, ImageGradient]:
    image = cv2.imread( img_path )
    # image = cv2.blur(image,(5,5))

    if FULLSCREEN:
        image = normalize_image_size(image, max_dimension=3440)
    else:
        image = normalize_image_size(image, max_dimension=720)
    return image, ImageGradient(image=image)


def _get_random_image_path(image_folder: str, previous: str | None) -> str:
    img_paths = [join(image_folder, f) for f in listdir(image_folder) if isfile(join(image_folder, f))]
    img_path = previous
    while img_path == previous:
        img_path = random.choice(img_paths)
    return img_path


def run_continuous_finch(image_folder: str, brush_sets: list[BrushSet]) -> Image | tuple[Image, bytes]:
    n_iterations_with_same_score = 0
    last_update_time = datetime.now()

    shared_state = State()

    thread = Thread(
        target=render_thread,
        name="rendering_thread",
        kwargs={
            "shared_state": shared_state,
            "fullscreen": FULLSCREEN,
            "show_diff": SHOW_DIFF,
            "debug": DEBUG
        }
    )
    thread.start()

    while not shared_state.flag_stop:
        shared_state.img_path = _get_random_image_path(image_folder, shared_state.img_path)
        shared_state.brush = random.choice(brush_sets)
        preload_brush_textures_for_brush_set( brush_set = shared_state.brush )

        logger.info(f"Drawing image {shared_state.img_path}")
        target_image, target_gradient = _prep_image(shared_state.img_path)
        if shared_state.specimen is None:
            shared_state.specimen = get_initial_specimen( target_image = target_image )
        fitness = get_fitness( specimen = shared_state.specimen, target_image = target_image )
        shared_state.score = 9999999
        generation_index = 0

        image_start_time = time.time()

        while (
            not shared_state.flag_stop
            and not shared_state.flag_next_image
            and time.time() - image_start_time < MAXIMUM_TIME_PER_IMAGE_SECONDS
        ):
            frame_start_time = time.time()
            generation_index += 1

            # Mutate a copy of the specimen
            new_specimen, new_fitness, new_score = iterate_image(
                shared_state.specimen,
                fitness,
                target_image,
                target_gradient,
                store_brushes=False
            )

            # Only keep the new version if it is an improvement
            if new_score >= shared_state.score:
                n_iterations_with_same_score += 1
            else:
                n_iterations_with_same_score = 0
                fitness = new_fitness
                shared_state.score = new_score
                shared_state.specimen = new_specimen
                shared_state.image_available = True

            current_update_time = datetime.now()
            shared_state.update_time_microseconds = ( current_update_time - last_update_time ).microseconds
            last_update_time = current_update_time

            report_string = (
                f'gen_{generation_index:06d}__dt_{shared_state.update_time_microseconds}_us__score_{shared_state.score}'
            )

            logger.debug( report_string )

            if is_drawing_finished(n_iterations_with_same_score, shared_state.score):
                break

            frame_time = time.time() - frame_start_time
            if frame_time < MINIMUM_STEP_TIME_SECONDS:
                time.sleep(MINIMUM_STEP_TIME_SECONDS - frame_time)

        shared_state.flag_next_image = False

    thread.join()

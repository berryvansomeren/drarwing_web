import logging
import math

import cv2

from finch.primitive_types import Image


logger= logging.getLogger(__name__)


def normalize_image_size( image : Image, max_dimension = 640 ) -> Image:
    height, width = image.shape[:2]
    if ( width <= 640 ) and ( height <= 640 ):
        logger.info( f"Image is not resized. Its size is ({width}*{height})." )
        return image
    aspect_ratio = width / height
    if width >= height :
        new_width = max_dimension
        new_height = int( new_width / aspect_ratio )
    else :
        new_height = max_dimension
        new_width = int( new_height * aspect_ratio )
    resized_image = cv2.resize( image, ( new_width, new_height ) )
    logger.info( f'Resized image from ({width}*{height}) to ({new_width}*{new_height}).' )
    return resized_image


def scale_to_dimension(image: Image, dimension: tuple[int, int]) -> Image:
    target_aspect_ratio = dimension[0] / dimension[1]
    image_aspect_ratio = image.shape[1] / image.shape[0]

    if target_aspect_ratio < image_aspect_ratio:
        # Y is the limiting factor, scale Y up to max and scale X accordingly
        image = cv2.resize(image, (int(dimension[1] * image_aspect_ratio), dimension[1]))
        # Crop X to fit
        remove_side = int((image.shape[1] - dimension[0]) / 2)
        image = image[:, remove_side:image.shape[1]-remove_side]
    elif target_aspect_ratio > image_aspect_ratio:
        # X is the limiting factor, scale X up to max and scale Y accordingly
        image = cv2.resize(image, (dimension[0], int(dimension[0] / image_aspect_ratio)))
        # Crop Y to fit
        remove_side = int((image.shape[0] - dimension[1]) / 2)
        image = image[remove_side:image.shape[0]-remove_side, :]

    # Final resize, in case the rounding caused some issues or the aspect ratio was already correct
    image = cv2.resize(image, dimension)
    return image


def get_scale_for_4k_from_shape( current_height, current_width ):
    # using a weird definition of 4k here,
    # so that we do not change aspect ratio,
    # but get approximately the same number of pixels
    target_n_pixels = 2160 * 3840
    aspect_ratio = current_width / current_height
    new_height = math.sqrt( target_n_pixels / aspect_ratio )
    scale = new_height / current_height
    return scale


def get_scale_for_4k_from_image( image ):
    return get_scale_for_4k_from_shape( *image.shape[:2] )

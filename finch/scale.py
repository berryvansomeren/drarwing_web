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

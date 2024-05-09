import enum

import cv2
import numpy as np
import colour

from finch.primitive_types import Image
from finch.image_utils import scale_image

DIFF_IMAGE_FACTOR = 2

class DifferenceMethod(enum.Enum):
    ABSOLUTE = enum.auto()
    RELATIVE = enum.auto()
    DELTAE = enum.auto()


def get_difference_image(
    specimen_image : Image, target_image : Image, method: DifferenceMethod = DifferenceMethod.ABSOLUTE
) -> Image:
    specimen_image_small = scale_image(specimen_image, 1 / DIFF_IMAGE_FACTOR)
    target_image_small = scale_image(target_image, 1 / DIFF_IMAGE_FACTOR)

    match method:
        case DifferenceMethod.ABSOLUTE:
            difference_image = _get_absolute_difference_image(specimen_image_small, target_image_small)
        case DifferenceMethod.RELATIVE:
            difference_image = _get_relative_difference_image(specimen_image_small, target_image_small)
        case DifferenceMethod.DELTAE:
            difference_image = _get_deltaE_difference_image(specimen_image_small, target_image_small)
        case _: raise NotImplementedError

    return scale_image(difference_image, DIFF_IMAGE_FACTOR)


def _get_absolute_difference_image( specimen_image : Image, target_image : Image ) -> Image:
    specimen_image_gray = cv2.cvtColor(specimen_image, cv2.COLOR_BGR2GRAY)
    target_image_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    return cv2.absdiff(specimen_image_gray, target_image_gray)


def _get_relative_difference_image( specimen_image : Image, target_image : Image ) -> tuple[Image, Image]:
    specimen_image_gray = cv2.cvtColor(specimen_image, cv2.COLOR_BGR2GRAY)
    target_image_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    diff_image = cv2.absdiff(specimen_image_gray, target_image_gray)
    max_vals = np.maximum(specimen_image_gray, target_image_gray, where=target_image_gray!=0)
    scaled_diff_image = np.multiply(np.divide(diff_image, max_vals), 255).astype("uint8")
    return scaled_diff_image


def _get_deltaE_difference_image( specimen_image : Image, target_image : Image ) -> tuple[Image, Image]:
    specimen_image_LAB = cv2.cvtColor(specimen_image, cv2.COLOR_BGR2LAB)
    target_image_LAB = cv2.cvtColor(target_image, cv2.COLOR_BGR2LAB)
    diff_image = colour.difference.delta_E_CIE1976(specimen_image_LAB, target_image_LAB)
    return diff_image.astype("uint8")

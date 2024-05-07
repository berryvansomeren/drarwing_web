import cv2
import numpy as np

from finch.primitive_types import Image


def get_absolute_difference_image( specimen_image : Image, target_image : Image ) -> Image:
    diff_image = cv2.absdiff(
        cv2.cvtColor(specimen_image, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    )
    return diff_image

import cv2
import numpy as np

from finch.primitive_types import Image


def get_absolute_difference_image( specimen_image : Image, target_image : Image ) -> Image:
    specimen_image_gray = cv2.cvtColor(specimen_image, cv2.COLOR_BGR2GRAY)
    target_image_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    return cv2.absdiff(specimen_image_gray, target_image_gray)


def get_relative_difference_image( specimen_image : Image, target_image : Image ) -> tuple[Image, Image]:
    specimen_image_gray = cv2.cvtColor(specimen_image, cv2.COLOR_BGR2GRAY)
    target_image_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    diff_image = cv2.absdiff(specimen_image_gray, target_image_gray)
    max_vals = np.maximum(specimen_image_gray, target_image_gray, where=target_image_gray!=0)
    scaled_diff_image = np.multiply(np.divide(diff_image, max_vals), 255).astype("uint8")
    return scaled_diff_image

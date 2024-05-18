import cv2
import math

from finch.primitive_types import Image, Point


class ImageGradient:
    def __init__(self, image: Image, blur_kernel_size=None, blur_magnitude=0):
        if blur_kernel_size is None:
            blur_kernel_size = int(min(image.shape[:2]) / 50)
        if blur_kernel_size % 2 == 0:
            blur_kernel_size += 1

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        dx = cv2.Scharr(gray, cv2.CV_32F, 1, 0)
        dy = cv2.Scharr(gray, cv2.CV_32F, 0, 1)

        blur_kernel_size_2d = (blur_kernel_size, blur_kernel_size)
        self._dx = cv2.GaussianBlur(dx, blur_kernel_size_2d, blur_magnitude)
        self._dy = cv2.GaussianBlur(dy, blur_kernel_size_2d, blur_magnitude)

    def get_direction(self, position: Point) -> float:
        dy = self._dy[position.y, position.x]
        dx = self._dx[position.y, position.x]
        direction = math.degrees(math.atan2(dy, dx))
        return direction

    def get_magnitude(self, position: Point) -> float:
        dy = self._dy[position.y, position.x]
        dx = self._dx[position.y, position.x]
        magnitude = math.hypot(dy, dx)
        return magnitude

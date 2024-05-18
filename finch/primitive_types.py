from dataclasses import dataclass
import numpy as np


Color = tuple[int, int, int]


@dataclass
class Point:
    x: int
    y: int

    def copy(self) -> "Point":
        return Point(self.x, self.y)

    def mult(self, factor: float) -> None:
        self.x = int(self.x * factor)
        self.y = int(self.y * factor)


FitnessScore = float
Image = np.ndarray

from dataclasses import dataclass
import numpy as np


Color = tuple[ int, int, int ]


@dataclass
class Point :
    x: int
    y: int


FitnessScore = float
Image = np.ndarray

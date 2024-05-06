from dataclasses import dataclass
import numpy as np


Color = tuple[ int, int, int ]


@dataclass
class Point :
    x: int
    y: int

    def copy( self ) -> "Point":
        return Point( self.x, self.y )


FitnessScore = float
Image = np.ndarray

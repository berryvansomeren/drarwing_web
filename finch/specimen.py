from dataclasses import dataclass, field

from finch.primitive_types import Image
from finch.brush import Brush


@dataclass
class Specimen :
    cached_image: Image

    # The brushes are basically the genes of the specimen.
    # We do not actually use them in the algorithm,
    # because we can directly draw changes on top of the cached image
    # But storing this info allows for better inspection,
    # and to later redraw the image with different settings, if pickled.
    # For that, see common.redraw.redraw_painting
    brushes: list[ Brush ] = field( default_factory = list )
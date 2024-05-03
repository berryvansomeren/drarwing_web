import logging
import math

import numpy as np

from finch.primitive_types import Image, Point
from finch.brush import Brush, get_global_brush_textures, draw_brush_on_image
from finch.scale import get_scale_for_4k_from_image
from finch.specimen import Specimen


logger = logging.getLogger(__name__)


def _redraw_painting(
        brushes : list[Brush],
        scale: float,
        result_image: np.ndarray,
) -> Image:

    """
    Redraws a painting by using scaled versions of the original brushes.
    As long as the brush texture is available at larger resolutions,
    this allows you to make higher resolution versions of your images.
    Even if some of the brushes are drawn at scales larger than the original texture resolution,
    the image detail improve drastically as the larger brushes are painted over with smaller images.
    """

    def int_scale(v):
        return int( v * scale )

    for brush in brushes:
        # note that brush width and height are expected to be equal
        brush.size = int_scale(brush.size)

        brush.position = Point(
            int_scale(brush.position.x),
            int_scale(brush.position.y),
        )

        draw_brush_on_image( brush, result_image )

    # As long as oversized brushes disappear in the background when they are painted over with smaller brushes,
    # having oversized brushes is not a problem.
    # logger.info(f'Encountered {n_oversized_brushes}/{len(brushes)} oversized brushes')
    return result_image


def redraw_painting_at_4k(
        specimen : Specimen,
):
    scale = get_scale_for_4k_from_image( specimen.cached_image )

    result_image_shape = (
        math.ceil( specimen.cached_image.shape[0] * scale ),
        math.ceil( specimen.cached_image.shape[1] * scale ),
        3
    )
    result_image = np.zeros( result_image_shape, dtype = np.uint8 )
    result_image.fill(255)

    result = _redraw_painting(
        specimen.brushes,
        scale,
        result_image
    )

    return result

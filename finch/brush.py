from dataclasses import dataclass
from enum import Enum, auto
import random

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, List

from finch.primitive_types import Color, Point, FitnessScore


ROOT_DIR                        = Path( __file__ ).parent.parent
DEFAULT_BRUSH_DIRECTORY         = ROOT_DIR / 'finch/brushes'


class BrushSet(Enum):
    Canvas = auto()
    Oil = auto()
    Sketch = auto()
    Watercolor = auto()


@dataclass
class Brush:
    color           : Color
    texture_index   : int
    position        : Point
    angle           : float
    size            : int


def str_to_brush_set( s : str ) -> BrushSet:
    return {
        'Oil' : BrushSet.Oil,
        'Canvas' : BrushSet.Canvas,
        'Sketch' : BrushSet.Sketch,
        'Watercolor' : BrushSet.Watercolor
    }[s]


def get_brush_size_for_fitness( fitness : FitnessScore, image_height : int, image_width : int ) -> int:
    # Note that the fitness score is actually the percentage of difference with the target image
    # The brush size is then simply a percentage of the size of the image, based on this difference,
    # and scaled with a configurable parameter.
    image_min_extend = min( image_height, image_width )
    scaled_brush_size = int( image_min_extend * fitness )
    brush_size = max( 1, scaled_brush_size )
    return brush_size


PRELOADED_BUSH_TEXTURES : Optional[List ] = None


def _set_global_brush_textures( brush_textures : List[np.ndarray ] ) -> None:
    global PRELOADED_BUSH_TEXTURES
    PRELOADED_BUSH_TEXTURES = brush_textures


def get_global_brush_textures() -> List[np.ndarray]:
    return PRELOADED_BUSH_TEXTURES


def _preload_brush_textures_from_path( directory_name : Path ) -> None:
    texture_paths = []
    for extension in [ '.jpg', '.png' ]:
        texture_paths.extend( list( directory_name.rglob( f'*{extension}' ) ) )
    textures = [ cv2.imread( str(texture_path) ) for texture_path in texture_paths ]
    textures = [ cv2.cvtColor( texture, cv2.COLOR_BGR2GRAY ) for texture in textures ]
    _set_global_brush_textures( textures )


def _brush_set_to_directory_path(brush_set: BrushSet) -> str:
    directory_name = {
        BrushSet.Oil : 'oil',
        BrushSet.Sketch : 'sketch',
        BrushSet.Canvas : 'canvas',
        BrushSet.Watercolor : 'watercolor'
    }[brush_set]
    directory_path = DEFAULT_BRUSH_DIRECTORY / directory_name
    return directory_path


def preload_brush_textures_for_brush_set( brush_set : BrushSet ) -> None:
    brush_directory_path = _brush_set_to_directory_path( brush_set )
    _preload_brush_textures_from_path( brush_directory_path )


def random_brush_texture_index():
    return random.choice( range( len( get_global_brush_textures() ) ) )


def draw_brush_on_image( brush : Brush, image : np.ndarray ) -> np.ndarray:
    image_height, image_width = image.shape[:2]

    brush_texture_original = get_global_brush_textures()[brush.texture_index ]
    brush_texture_scaled = cv2.resize( brush_texture_original, (brush.size, brush.size) )
    brush_height, brush_width = brush_texture_scaled.shape[:2]

    transformation_matrix = cv2.getRotationMatrix2D( (brush_width/2, brush_height/2), brush.angle, 1 )
    brush_texture_rotated = cv2.warpAffine( brush_texture_scaled, transformation_matrix, (brush_width, brush_height))

    alpha = brush_texture_rotated.astype( float ) / 255.0
    alpha_3 = np.dstack( (alpha, alpha, alpha) )

    foreground = np.full_like(brush_texture_rotated, brush.color, shape=(*brush_texture_rotated.shape, 3))

    # Where to start drawing, in Canvas Space
    draw_y = int( brush.position.y - brush_width / 2 )
    draw_x = int( brush.position.x - brush_height / 2 )

    # Adjust ROI to make sure we do not cross the borders of the canvas space
    y_min = max( draw_y, 0 )
    y_max = min( draw_y + brush_height, image_height )
    x_min = max( draw_x, 0 )
    x_max = min( draw_x + brush_width, image_width )

    # background is the original image, foreground is the brush on top
    background_subsection = image[y_min:y_max, x_min:x_max]

    # We have to adjust the roi to the size of the brush matrix
    foreground_subsection = foreground[
        y_min - draw_y : y_max - draw_y,
        x_min - draw_x : x_max - draw_x
    ]
    alpha_subsection = alpha_3[
        y_min - draw_y : y_max - draw_y,
        x_min - draw_x : x_max - draw_x
    ]

    composite = background_subsection * (1 - alpha_subsection) + foreground_subsection * alpha_subsection
    image[ y_min:y_max, x_min:x_max ] = composite
    return image

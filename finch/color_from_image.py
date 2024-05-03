from finch.primitive_types import Color, Image, Point


def get_color_from_image( image : Image, position : Point ) -> Color:
    color_raw = image[ position.y, position.x ]
    color = ( int(color_raw[0]), int(color_raw[1]), int(color_raw[2]) )
    return color

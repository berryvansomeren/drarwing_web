import logging

import cv2

from finch.run import set_global_config, Config, DEFAULT_INPUT_IMAGE_PATH, run_finch


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig( level = logging.DEBUG )
    logging.getLogger( 'PIL.Image' ).setLevel( logging.WARNING )
    set_global_config( Config.DEBUG )
    path = str( DEFAULT_INPUT_IMAGE_PATH / 'new/10.jpg' )
    image = cv2.imread( path )
    assert image is not None
    brush_set_name = 'Canvas'
    run_finch( image = image, brush_set_name = brush_set_name )

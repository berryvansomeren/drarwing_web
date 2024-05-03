import base64
import logging
import sys

import cv2
from flask import Flask, jsonify, request as flask_request, Request, Response
from flask_cors import CORS
import numpy as np
from finch.main import run_finch, set_global_config, Config
from finch.memory_size import get_size_mib


logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

CORS_HEADERS = {
    'Access-Control-Allow-Origin' : '*',
    'Access-Control-Allow-Methods' : 'POST, OPTIONS',
    'Access-Control-Allow-Headers' : 'Content-Type',
    'Access-Control-Max-Age' : '3600'
}

KEY_RESULT_IMAGE = 'result_image'
KEY_RESULT_GIF = 'result_gif'

def make_response( data : dict, code : int ) -> Response:
    data.update({ 'status_code' : code })
    response = jsonify(data)
    response.status_code = code
    response.headers.update( CORS_HEADERS )

    response_size_b = response.calculate_content_length()
    response_size_mib = response_size_b / ( 1024 * 1024 )
    size_limit_mib = 30
    logging.info( f'Response size is {response_size_mib} MiB, limit is {size_limit_mib} MiB.' )

    if response_size_mib > size_limit_mib:
        logging.info(f'Response size too big!')
        response = make_error_response( 'Result too big to return... Try different settings and images!' )
    else:
        logger.info( f'Made Response with keys {data.keys()} - {code}.' )
    return response


def make_error_response( message : str ) -> Response:
    code = 400
    logger.info( f'Made Error Response: Error: {message} - {code}.' )
    return make_response( { 'error' : message }, code )


def log_size(data : dict) -> None:
    image_size_mib = get_size_mib(data[KEY_RESULT_IMAGE])
    gif_size_mib = get_size_mib(data[KEY_RESULT_GIF])
    combined_size_mib = image_size_mib + gif_size_mib

    logger.info(f"Image size: {image_size_mib}")
    logger.info(f"GIF size: {gif_size_mib}")
    logger.info(f"Combined size: {combined_size_mib}")


def handle_request( request : Request ) -> Response:
    logging.basicConfig( level = logging.DEBUG )
    logging.getLogger( 'PIL.Image' ).setLevel( logging.WARNING )
    set_global_config( Config.PROD )

    if 'brush_set' not in request.form:
        return make_error_response( 'No Brush Set specified in request.' )
    brush_set = request.form[ 'brush_set' ]

    if 'image' not in request.files :
        return make_error_response( 'No Image specified in request.' )
    try :
        image_file = request.files[ 'image' ]
        image_data = image_file.read()
        np_array_raw = np.frombuffer( image_data, np.uint8 )
        image = cv2.imdecode( np_array_raw, cv2.IMREAD_COLOR )
    except Exception:
        logger.exception('Could not parse image data.')
        return make_error_response( 'Could not parse image data.' )

    try:
        result = run_finch( image = image, brush_set_name = brush_set )
    except Exception:
        logger.exception( 'Processing - FAILED' )
        return make_error_response( 'Process on server failed. (The Developer is notified)' )

    has_gif = isinstance( result, tuple )
    if has_gif:
        result_image, result_gif = result
    else:
        result_image = result

    success, result_image_encoded = cv2.imencode( '.png', result_image )
    if not success:
        return make_error_response( 'Process succeeded, but failed to encode the result.' )
    result_image_base64_string = base64.b64encode(result_image_encoded).decode('utf-8')

    if not has_gif:
        return make_response( { 'result_image' : result_image_base64_string }, 200 )

    result_gif_base64_string = base64.b64encode( result_gif ).decode('utf-8')
    response_data = {
        KEY_RESULT_IMAGE : result_image_base64_string,
        KEY_RESULT_GIF : result_gif_base64_string,
    }
    log_size( response_data )
    return make_response( response_data, 200 )


# ----------------------------------------------------------------
# For local testing

@app.route('/', methods=['POST'])
def flask_handle_request() -> Response:
    return handle_request(flask_request)


if __name__ == '__main__':
    app.run()

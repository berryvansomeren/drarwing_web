import io
import logging

import cv2
import imageio

from finch.memory_size import get_size_mib
from finch.primitive_types import Image


logger = logging.getLogger(__name__)


def make_gif(result_frames : list[Image]) -> bytes:
    logger.info( f'Creating GIF.' )

    FPS = 5
    FINAL_FRAME_REPEAT_SECONDS = 3
    FINAL_FRAME_REPEAT_FRAMES = FPS * FINAL_FRAME_REPEAT_SECONDS

    n_frames_original = len(result_frames)
    n_frames_target = 50
    needs_skips = n_frames_original > n_frames_target

    logger.info( f'Got {n_frames_original} input frames.' )
    logger.info( f'Target is {n_frames_target} output frames.' )

    if needs_skips:
        n_frames_to_delete = n_frames_original - n_frames_target
        # add 1 because we do not want to delete the last frame
        frame_interval_to_delete = n_frames_original // n_frames_to_delete
        logger.info( f'Skipping every {frame_interval_to_delete} frames from the back.' )
    else:
        logger.info( f'No skips needed!' )

    n_frames_result = 0
    gif_buffer = io.BytesIO()
    with imageio.get_writer( gif_buffer, format = '.gif', mode = 'I', loop=0, fps = FPS ) as writer :
        for i, image in enumerate( result_frames ):
            # We skip certain frames to limit the number of output frames
            # We count the distance from the end of the list,
            # So that we don't remove frames too close to the end of the list
            if needs_skips:
                if i > 0 and ( n_frames_original - i ) % frame_interval_to_delete == 0:
                    logger.info(f'- Skipping frame {i}.')
                    continue
            n_frames_result += 1
            image_rgb = cv2.cvtColor( image, cv2.COLOR_BGR2RGB )
            writer.append_data( image_rgb )
        for i in range( FINAL_FRAME_REPEAT_FRAMES ):
            writer.append_data( image_rgb )

    logger.info(f'Result has {n_frames_result} + {FINAL_FRAME_REPEAT_FRAMES} frames.')

    original_gif = gif_buffer.getvalue()
    original_size_mib = get_size_mib(original_gif)
    logger.info(f'GIF is {original_size_mib} MiB.')

    # optimized_gif = gifsicle_optimize_in_memory(original_gif)
    # size_bytes_optimized = get_size_mib(optimized_gif)
    #
    # logger.info(f'Optimizing the GIF brought it from {original_size_mib} MiB to {size_bytes_optimized} MiB')

    return original_gif


# ================================================================
# We are currently not using gifsicle,
# because we cannot easily install it inside a GCF
#
# def gifsicle_optimize_in_memory(
#         gif_data: bytes,
#         colors: int = 256,
#         options: list[str] | None = None
# ) -> bytes:
#     if options is None:
#         options = []
#
#     if "--optimize" not in options:
#         options.append("--optimize")
#
#     TESTING_ON_WINDOWS = False
#     if TESTING_ON_WINDOWS:
#         exe = "C:/Users/Berry/Downloads/gifsicle-1.95-win64/gifsicle"
#     else:
#         exe = "gifsicle"
#
#     command = [ exe, *options, "--colors", str( colors ) ]
#     try:
#         proc = subprocess.Popen(
#             command,
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )
#         result_gif_data, stderr_data = proc.communicate(input=gif_data)
#         if stderr_data:
#             raise Exception(stderr_data.decode())
#
#     except FileNotFoundError:
#         raise FileNotFoundError("The gifsicle library was not found on your system.")
#
#     return result_gif_data
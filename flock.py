from finch.run_continuous import run_continuous_finch, BrushSet

import logging

LOGLEVEL = logging.DEBUG

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(LOGLEVEL)
# Streaming Handler
c_handler = logging.StreamHandler()
c_handler.setLevel(LOGLEVEL)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


image_folder = "_input_images"

result = run_continuous_finch(
    image_folder = image_folder,
    brush_sets = [brush_set for brush_set in BrushSet]
)

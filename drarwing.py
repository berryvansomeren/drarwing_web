from finch.run import run_finch_generator, BrushSet

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


image_folder = "images"

result = run_finch_generator(
    image_folder = image_folder,
    brush_sets = [brush_set for brush_set in BrushSet if brush_set != BrushSet.Sketch]
)

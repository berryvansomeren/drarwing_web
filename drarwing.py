from finch.run import Config, run_finch_generator, set_global_config, str_to_brush_set
from os import listdir
from os.path import isfile, join

import logging

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Streaming Handler
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


# set_global_config(Config.DEBUG)
image_folder = "images"
img_paths = [join(image_folder, f) for f in listdir(image_folder) if isfile(join(image_folder, f))]
print(img_paths)
brush_set_name = 'Canvas'
brush_set = str_to_brush_set( brush_set_name )

result = run_finch_generator(
    target_images = img_paths,
    brush_set = brush_set
)

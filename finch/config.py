from enum import Enum, auto


class Config(Enum):
    DEBUG = auto()
    PROD = auto()


def set_global_config( config : Config ) -> None:
    global WRITE_OUTPUT
    global WRITE_PICKLE
    global MAKE_GIF
    if config == Config.DEBUG:
        WRITE_OUTPUT = True
        WRITE_PICKLE = False
        MAKE_GIF = True
    else:
        WRITE_OUTPUT = False
        WRITE_PICKLE = False
        MAKE_GIF = True

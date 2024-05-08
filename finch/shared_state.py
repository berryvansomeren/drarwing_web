from dataclasses import dataclass

from finch.brush import Brush
from finch.specimen import Specimen


@dataclass
class State:
    img_path: str | None = None
    brush: Brush | None = None

    specimen: Specimen | None = None
    score: int = 99999999

    image_available: bool = False
    update_time_microseconds: int = 0

    lock_image: bool = False

    flag_stop: bool = False
    flag_next_image: bool = False

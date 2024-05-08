import cv2
import time

from finch.shared_state import State

WINDOW_NAME = "drarwing_continuous"
DIFF_WINDOW_NAME = "drarwing_continuous_diff"
MIN_FRAME_DURATION = 1/60


def _window_exists(window_name: str):
    try:
        return cv2.getWindowProperty(window_name, 0) >= 0
    except:
        return False


def render_thread(shared_state: State, fullscreen: bool = True, show_diff: bool = False, debug: bool = False):
    if fullscreen:
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.namedWindow(WINDOW_NAME)

    if show_diff:
        cv2.namedWindow(DIFF_WINDOW_NAME)

    show_diff_in_main_window = False

    last_frame = time.time()
    last_frame_duration = -1.0
    while (
        not shared_state.flag_stop
        and _window_exists(WINDOW_NAME)
        and (not show_diff or _window_exists(DIFF_WINDOW_NAME))
    ):
        if shared_state.image_available:
            main_image = (
                cv2.cvtColor(shared_state.specimen.diff_image, cv2.COLOR_GRAY2BGR)
                if show_diff_in_main_window
                else shared_state.specimen.cached_image
            )

            if debug or shared_state.lock_image:
                main_image = main_image.copy()
                if debug:
                    main_image = cv2.putText(
                        main_image,
                        f"{shared_state.img_path}-{shared_state.brush.name} "
                        f"{shared_state.update_time_microseconds} us, {shared_state.score} score "
                        f'{round(1 / last_frame_duration) if last_frame_duration > 0 else "inf"} fps',
                        (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        1,
                        cv2.LINE_AA
                    )
                if shared_state.lock_image:
                    main_image = cv2.putText(
                        main_image,
                        "LOCKED",
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        1,
                        cv2.LINE_AA
                    )

            cv2.imshow(WINDOW_NAME, main_image)

            if show_diff:
                cv2.imshow(DIFF_WINDOW_NAME, shared_state.specimen.diff_image)

            key = cv2.waitKey(1)
            if key > -1:
                match key:
                    case 100: show_diff_in_main_window = not show_diff_in_main_window
                    case 108: shared_state.lock_image = not shared_state.lock_image  # "l"
                    case 110: shared_state.flag_next_image = True  # "n"
                    case _: break

        now = time.time()
        last_frame_duration = now - last_frame
        last_frame = now
        if last_frame_duration < MIN_FRAME_DURATION:
            time.sleep(MIN_FRAME_DURATION - last_frame_duration)

    shared_state.flag_stop = True
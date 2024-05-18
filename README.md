
# Drarwing as a continuous form of art!

This application takes Berry van Someren's fantastic drarwing application, and turns it into a continuous and
ever changing form of art designed to be displayed.

Check out the following links to Berry:

- [GitHub](https://github.com/berryvansomeren)
- [Website](https://www.berryvansomeren.com/)

And his project:

- [GitHub](https://github.com/berryvansomeren/drarwing_web)
- [Blog](https://www.berryvansomeren.com/posts/drarwing_web)


# Continous drarwing

A new extension to this code base is the option to run Drarwing continuously. For this, the program `flock.py` is
added in the root of the repo. In that file, you can configure the folder where images are read from. You can also
configure the set of Brushes that is used to randomly select from.

## Tweaking for your application

If you need to tweak some things, there are some constants configured in `finch/run_continuous.py`:
- `MAXIMUM_TIME_PER_IMAGE_SECONDS`:
    This is the maximum time spent on generating the image. Note that the image may be finished before. This excludes
    the time spent displaying the finished image.
- `MINIMUM_STEP_TIME_SECONDS`:
    This is the minimum time spent putting down a single brush stroke. Effectively, this parameter can be used to
    slow down the drawing if it is going to fast for your taste. Note that it is a minimum time, a brush stroke may be
    slower than this parameter.
- `WAIT_BETWEEN_IMAGES_SECONDS`:
    This is the time spent showing the finalized image.
- `DIFF_METHOD`:
    This allows selection of what difference method is used. There are three options:
    - `DifferenceMethod.ABSOLUTE`:
        The original approach. Absolute difference between grayscale values. This is the fastest method, but it does not
        give great results when two a different color of similar brightness is already present in the image. It also
        does not perform well when "redrawing" dark parts of the image, which is not a problem when drawing on white,
        but it is when drawing over an existing image.
    - `DifferenceMethod.RELATIVE`:
        This method is similar to the absolute method, but the result is scaled to the highest-brightness value of the
        pixels. Effectively, it becomes the "percentage of difference" between the target images and the current state.
        This still does not take colour differences into account, but it performs much better in dark parts of the
        images.
    - `DifferenceMethod.DELTAE`:
        This method uses the [https://en.wikipedia.org/wiki/Color_difference](CIELAB Delta-E) approach to determine
        differences, in our case CIE76 as the nuances of later versions are not too relevant for the blunt approach we
        take. This converts the images to the CIELAB colour space and calculates the Euclidean distance between those.
        This method is designed specifically to be as close as possible to how humans experience colour differences. It
        is however the slowest of the three by quite a bit.
- `FULLSCREEN`:
        Whether to run the application fullscreen or in a small image for faster testing purposes

Further tweaking to the speed-wise performance can be done with the `DIFF_IMAGE_FACTOR` parameters in
`finch/difference_image.py` and `finch/generate.py` - these scale down the difference image before performing expensive
operations on it in order to speed things up. The idea is that the brush strokes are so blunt, we don't need a super
detailed difference image to get virtually the same results. It may however cause some detrimental results to the
quality of the final image.

## Convenience and interactive controls

As this is an application with a "GUI", we can add some convenience features. These are controlled through the keyboard.

There are three image modes:
- `m`: Show the **m**ain image, the drawing being made. This is (naturally) the default
- `d`: Show the **d**ifference image, the calculated difference between the original image and the current drawing
- `o`: Show the **o**riginal image

Furthermore, the following keys are available:
- `i`: Show debug **i**nformation such as filenames, used brush and performance metrics
- `l`:
    **L**ock the image. This can have two effects: When selected while drawing, it prevents the drawing from being
    "finished", it will continued to be updated beyond the target score or timelimits. If selected while showing the
    finished image, it will merely prevent automatically rotating to the next image.
- `n`: Select the **n**ext image. Note that this ignores the locked mode.

Press `ESCAPE` to end the application

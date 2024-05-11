
# Drarwing on the Web!

**The blogpost and online version can be found [HERE](https://www.berryvansomeren.com/posts/drarwing_web)!** ✨

My genetic drawing program Drarwing has been optimized and streamlined so that it runs better and is easier to use,
and is now served on the web via Google Cloud Functions, making it accessible directly from any web browser.

<div align="center">
    <img src="./_doc/finch_via_drarwing_web_canvas_gif.gif" width="70%">
</div>

---

# Gallery

Some examples of results. All input images are from _[unsplash.com](https://unsplash.com/)_

<div align="center">
    <div >
        <img src="./_doc/butterfly.gif" width="40%">
        <img src="./_doc/butterfly.png" width="40%">
    </div>
    <div >
        <img src="./_doc/tiger.gif" width="40%">
        <img src="./_doc/tiger.png" width="40%">
    </div>
    <div >
        <img src="./_doc/frog.gif" width="40%">
        <img src="./_doc/frog.png" width="40%">
    </div>
    <div >
        <img src="./_doc/owl.gif" width="40%">
        <img src="./_doc/owl.png" width="40%">
    </div>
</div>

---

# BLOG: Some Nerdy Details

While the performance of Drarwing has drastically improved,
I did an interesting experiment for potentially improving it even further.
Drarwing uses an evolutionary algorithm, which includes a "selection" phase
to select which "specimen" get to live in the next "generation" of the "population".
Drarwing simply starts with a single specimen, copies it, mutates the copy,
and then checks if the copy is an improvement over the last version -
effectively using a population size of 2.
I wondered what would happen if we used a population size of 1.

Since the mutations are guided in a way that *should* improve the result,
we could try skipping the check whether the new version is an improvement.
However, in reality, not every mutation is an improvement.
We use single pixel values to determine condidate locations for new brush strokes.
However, when placing the brush stroke, not only that particular pixel is affected,
but also many pixels around it.
As a result, placing a new brush stroke might make a specimen worse than its predecessor.
This is not always a problem; it's okay if the fitness score temporarily becomes worse again,
as long is it generally improves. And this happens for many images, but not all.

Especially for images with a lot of fine grained details, or small highlights,
the evolutionary algorithm can get stuck in a loop,
where in for example 20 generations it keeps circling around the same area,
continuously overdrawing it's previous changes.
You could try to detect such a loop, but it's just way simpler to use a population size larger than 1,
and simply check for improvement.
Unfortunately, creating copies of the best specimen of the previous generation,
is quite expensive and makes the process as a whole roughly 5 times slower, which is really unfortunate.

On the other hand, without such a check to prevent getting stuck in a loop, the algorithm was not able to generate this beauty:

<div align="center">
    <img src="./_doc/fox_via_drarwing_web.png" width="70%">
</div>

---

# Continous drarwing

A new extension to this code base is the option to run Drarwing continuously. For this, the program `continuous.py` is
added in the root of the repo. In that file, you can configure a folder where images are read from. You can also
configure the set of Brushes that is rotated through.

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
        take. This converts the images to the CIELAB colour space and calculates the euclidean distance between those.
        This method is designed specifically to be as close as possible to how humans experience colour differences.
        This method is however the slowest of the three by some margin.
- `FULLSCREEN`:
        Whether to run the application fullscreen or in a small image for faster testing purposes

Further tweaking can be done with the `DIFF_IMAGE_FACTOR` parameters in `finch/difference_image.py` and
`finch/generate.py` - these scale down the difference image before performing expensive operations on it in order to
speed things up. The idea is that the brush strokes are so blunt, we don't need a super detailed difference image to get
virtually the same results.

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


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

# pymandelbrot
Python/GLSL Mandelbrot visualizer.

Mostly a rewrite of my Kotlin mandelbrot visualizer to make working on it easier. I like kotlin and all, but its a pain in the butt to move the code anywhere.
With python the code just works as long as the libraries are installed.

At any rate the goal with this version was to allow me to code up different fractal algorithms. I wanted to try the burning ship function and the orbit trap coloring scheme, among other things.
This version also has the ability to generate rough Buddhabrot images. It would be nice to add code to take screenshots of each frame to create animations, like the kotlin version does.

Here's an example of the buddhabrot output (cropped and rotated from original):

![146907160-f4f6b351-0fa3-48d4-ae4f-4298f6b3cb20](https://user-images.githubusercontent.com/10580033/174425091-c992b340-7822-4209-8612-da0b61823101.png)

I've lost interest in this program currently but there are plans to add a GUI to make navigation easier. Basically it would take all the keyboard functions the kotlin version had (like bookmarked locations) and make them point-and-click items.

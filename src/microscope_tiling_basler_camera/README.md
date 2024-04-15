# Tiling Example with Basler Camera

*By Colby Sparks*

Often we want to capture high resolution images of samples which we cannot fit into a single camera frame.
In situations like this it makes sense to create an image tileset: a collection of images which when joined
form an ultra-high resolution representation of the sample in question.

This example showcases a simple technique for creating an image tileset, allowing a user to specify the top left and bottom right corners of the region they'd like to scan, and also the desired percentage of overlap between am
image and its horizontal and vertical neighbours. The example also illustrates how to control a Basler camera 
using the pypylon API.

## Hardware Requirements
The full example requires a Zaber microscope and Basler camera + objective. If you would like to use a different 
camera, you can implement your own camera wrapper class following the example of the `basler_camera_wrapper.py`

## Dependencies / Software Requirements / Prerequisites
> The script uses `pipenv` to manage virtual environment and dependencies:
> ```
> python3 -m pip install -U pipenv
> ```
> The dependencies are listed in Pipfile.

## Configuration / Parameters
> Edit the following constants in the script to fit your setup before running the script:
> - `SERIAL_PORT`: the serial port that your device is connected to.
> For more information on how to identify the serial port,
> see [Find the right serial port name](https://software.zaber.com/motion-library/docs/guides/find_right_port).
> - `SAVE_FOLDER`: the folder in which the tiled images will be saved
> - `PIXEL_WIDTH_MICRONS`: real-world measurement for pixel width (estimated from pixel calibration)
> - `PIXEL_HEIGHT_MICRONS`: real-world measurement for pixel height (estimated from pixel calibration)
> - `CAMERA_ROTATION_RAD`: camera rotation on z axis (axis orthogonal to plane defined by xy stage)
> - `TOP_LEFT`: top left point of sample region (can be copied directly from microscope app in zaber launcher)
> - `BOTTOM_RIGHT`: bottom right point of sample region (also can be copied)
> whatever your camera orientation, it must be true that `TOP_LEFT.x` <= `BOTTOM_RIGHT.x` and
> - `TOP_LEFT.y` > `BOTTOM_RIGHT.y` (ie. top left and top right with respect to microscope xy stage coords)
> - `OVERLAP_H`: desired decimal percentage of horizontal overlap between neighbouring tiles
> - `OVERLAP_V`: desired decimal percentage of vertical overlap between neighbouring tiles
> - `RUN_BEST_EFFORT_STITCHING`: attempt to stitch tiles together using openCV's Stitcher class (more on openCV's high level stitching API [here](https://docs.opencv.org/4.x/d8/d19/tutorial_stitcher.html))
> - `RUN_NAIVE_TILING`: concatenate tiles together into single image--this should only be used with 0 horizontal
> and vertical overlap

## Running the Script
> To run the script:
> ```
> cd src/microscope_tiling_basler_camera/
> pipenv install
> pipenv run python main.py
> ```

# Explaining the Central concept
This section explains the central concept or idea of the example in plain language.
There could be multiple subsections that talk about different parts of the code that supports
the central concept.

Sometimes it is useful to reference snippets of code in your explanation.
Use a [permanent link](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-a-permanent-link-to-a-code-snippet)
to some lines of code in the repository after at least one commit, and GitHub will link directly to the snippet.

## Optional Troubleshooting Tips or FAQ
Can provide additional information as needed.

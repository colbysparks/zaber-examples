"""Example code entry point."""

import os
import numpy as np
import cv2

from numpy.typing import NDArray
from cv2.typing import MatLike
from zaber_motion.ascii import Connection, AxisGroup
from zaber_motion import Measurement, Units
from zaber_motion.microscopy import Microscope
from .basler_camera_wrapper import (
    BaslerCameraWrapper,
    ImageCaptureError,
)
from .example_util import try_stitch_images, join_tiles
from .path_builder import PathBuilder

# user-specified params
SERIAL_PORT: str = "/dev/tty.usbserial-AB0PG6A5"
PIXEL_WIDTH_MICRONS: float = 3.0177054668168553
PIXEL_HEIGHT_MICRONS: float = 3.0177054668168553
CAMERA_ROTATION_RAD: float = 0.045226578

# TODO: reset point values to 0 after someone tests this example
# TOP_LEFT and BOTTOM_RIGHT are np.array([x, y]) where xy are microscope plate coords
# make sure to specify units
TOP_LEFT: NDArray[np.float64] = np.array([51.6696875, 48.70765625])
BOTTOM_RIGHT: NDArray[np.float64] = np.array([55.06625, 44.0253125])
POINTS_UNITS: Units = Units.LENGTH_MILLIMETRES  # units for TOP_LEFT and BOTTOM_RIGHT
OVERLAP_H: float = 0.5
OVERLAP_V: float = 0.5

# image capture
SAVE_FOLDER: str = "tiles"
RUN_BEST_EFFORT_STITCHING: bool = True
RUN_NAIVE_TILING: bool = True

# non user-controlled params
CENTRE: NDArray[np.float64] = TOP_LEFT + (BOTTOM_RIGHT - TOP_LEFT) / 2.0
EPSILON: float = 0.0000001


def main() -> None:
    """Run microscope tiling example."""
    check_user_specified_params()

    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    with Connection.open_serial_port(SERIAL_PORT) as connection:
        connection.detect_devices()
        microscope: Microscope = Microscope.find(connection)
        if microscope.plate is not None:
            plate: AxisGroup = microscope.plate
        else:
            raise RuntimeError("Microscope plate is None.")

        if not microscope.is_initialized():
            print("Initializing microscope.")
            microscope.initialize()
        print("Microscope is initialized.")

        camera: BaslerCameraWrapper = BaslerCameraWrapper()

        path_builder: PathBuilder = PathBuilder(
            PIXEL_WIDTH_MICRONS,
            PIXEL_HEIGHT_MICRONS,
            CAMERA_ROTATION_RAD,
            camera.get_frame_width(),
            camera.get_frame_height(),
        )
        tiling_path = path_builder.get_path_snake(
            TOP_LEFT, BOTTOM_RIGHT, POINTS_UNITS, OVERLAP_H, OVERLAP_V
        )

        tiles = capture_images(tiling_path, camera, plate)
        num_rows: int = len(tiling_path)

        if RUN_BEST_EFFORT_STITCHING:
            try:
                try_stitch_images(tiles, num_rows)
            except AssertionError as e:
                print("Stitching failed with AssertionError: ", e)
            except RuntimeError as e:
                print("Stitching failed with RuntimeError: ", e)
        if RUN_NAIVE_TILING:
            join_tiles(tiles, num_rows)


def capture_images(
    tiling_path: PathBuilder.MotionPath,
    camera: BaslerCameraWrapper,
    plate: AxisGroup,
) -> list[list[MatLike]]:
    """
        Move along provided path, capturing and saving an image at each point.

    Args:
        tiling_path (PathBuilder.MotionPath): the path generated from pathbuilder
        camera: the camera which will be used to take pictures
        plate: the microscope plate

    Raises:
        RuntimeError: raised if camera API fails to capture an image for whatever reason

    Returns:
        list[list[MatLike]]: list of rows of captured images
    """
    tiles: list[list[MatLike]] = []
    idx_y: int
    grid_row: list[tuple[float, float]]
    for idx_y, grid_row in enumerate(tiling_path):
        tile_row: list[MatLike] = []
        idx_x: int
        point: tuple[float, float]
        for idx_x, point in enumerate(grid_row):
            plate.move_absolute(
                Measurement(point[0], Units.LENGTH_MICROMETRES),
                Measurement(point[1], Units.LENGTH_MICROMETRES),
            )
            try:
                img = camera.grab_frame()
            except ImageCaptureError as e:
                raise RuntimeError from e

            tile_row.append(img)
            filename: str = SAVE_FOLDER
            if not idx_y & 1:
                filename += f"/tile_{idx_y}_{idx_x}.png"
            else:
                filename += f"/tile_{idx_y}_{len(grid_row) - idx_x - 1}.png"
            cv2.imwrite(filename, img)

        if not idx_y & 1:
            tile_row.reverse()
        tiles.append(tile_row)
    return tiles


def check_user_specified_params() -> None:
    """Verify that user-specified params are valid and provide feedback."""
    assert TOP_LEFT[0] <= BOTTOM_RIGHT[0], "It must be that TOP_LEFT.x <= BOTTOM_RIGHT.x"
    assert TOP_LEFT[1] >= BOTTOM_RIGHT[1], "It must be that TOP_LEFT.y >= BOTTOM_RIGHT.y"

    assert PIXEL_WIDTH_MICRONS > 0.0, "PIXEL_WIDTH_MICRONS must be greater than 0"
    assert PIXEL_HEIGHT_MICRONS > 0.0, "PIXEL_WIDTH_MICRONS must be greater than 0"
    if RUN_BEST_EFFORT_STITCHING and (OVERLAP_H < 0.1 or OVERLAP_V < 0.1):
        print("Warning: At least 0.1 horizontal and vertical overlap is recommended for stitching")
    if RUN_NAIVE_TILING and (OVERLAP_H > 0.0 or OVERLAP_V > 0.0):
        print("Warning: 0.0 overlap is suggested for naive tiling")

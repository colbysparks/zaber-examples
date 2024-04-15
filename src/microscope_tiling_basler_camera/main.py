import numpy as np
import cv2
import os

from cv2.typing import MatLike
from zaber_motion.ascii import Connection, AxisGroup
from zaber_motion import Measurement, Units
from zaber_motion.microscopy import Microscope
from microscope_tiling_basler_camera.basler_camera_wrapper import BaslerCameraWrapper, ImageCaptureError
from example_util import is_even, try_stitch_images, join_tiles
from path_builder import PathBuilder

# user controlled params

SERIAL_PORT: str = "COMX"
SAVE_FOLDER: str = "tiles"
PIXEL_WIDTH_MICRONS: float = 1.0
PIXEL_HEIGHT_MICRONS: float = 1.0
CAMERA_ROTATION_RAD: float = 0.0

# points can be copied from the microscope app in zaber launcher
TOP_LEFT: MatLike = np.array([0.0, 0.0])
BOTTOM_RIGHT: MatLike = np.array([10.0, 0.0])
UNITS_POINTS: str = Units.LENGTH_MILLIMETRES
OVERLAP_H: float = 0.0
OVERLAP_V: float = 0.0

RUN_BEST_EFFORT_STITCHING: bool = True
RUN_NAIVE_TILING: bool = True

# non user-controlled params

CENTRE: MatLike = TOP_LEFT + (BOTTOM_RIGHT - TOP_LEFT) / 2.0
EPSILON: float = 0.0000001


def main():
    with Connection.open_serial_port(SERIAL_PORT) as connection:
        connection.detect_devices(identify_devices=True)
        microscope: Microscope = Microscope.find(connection)
        plate: AxisGroup = microscope.plate

        print("Homing microscope plate")
        plate.home()

        # set up basler camera wrapper
        camera: BaslerCameraWrapper = BaslerCameraWrapper()
        path_builder: PathBuilder = PathBuilder(
            PIXEL_WIDTH_MICRONS,
            PIXEL_HEIGHT_MICRONS,
            CAMERA_ROTATION_RAD,
            camera.get_frame_width(),
            camera.get_frame_height(),
        )
        
        # get tiling path
        tiling_path = path_builder.get_path_snake(
            TOP_LEFT, BOTTOM_RIGHT, UNITS_POINTS, OVERLAP_H, OVERLAP_V
        )

        if not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)

        # capture images
        tiles: list[MatLike] = []
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
                    print(e)
                    raise RuntimeError

                tile_row.append(img)
                filename: str = SAVE_FOLDER
                if is_even(idx_y):
                    filename += "/tile_{0}_{1}.png".format(idx_y, idx_x)
                else:
                    filename += "/tile_{0}_{1}.png".format(idx_y, len(grid_row) - idx_x - 1)
                cv2.imwrite(filename, img)
            if not is_even(idx_y):
                tile_row.reverse()
            tiles.append(tile_row)

        # optional: run best effort stitching and/or image tiling
        num_rows: int = len(tiling_path)
        if RUN_BEST_EFFORT_STITCHING:
            try:
                try_stitch_images(tiles, num_rows)
            except RuntimeError:
                print("Stitching failed")

        if RUN_NAIVE_TILING:
            join_tiles(tiles, num_rows)


if __name__ == "__main__":
    main()

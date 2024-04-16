import numpy as np
from numpy.typing import NDArray
from cv2.typing import MatLike
from example_util import convert_length_to_microns
from zaber_motion import Units


class PathBuilder:
    Path = list[list[tuple[float, float]]]

    def __init__(
        self,
        pxl_w_um: float,
        pxl_h_um: float,
        camera_rotation: float,
        cam_frame_width: float,
        cam_frame_height: float,
    ):
        self._pxl_w_um = pxl_w_um
        self._pxl_h_um = pxl_h_um
        self._rotation_matrix_2d = np.array(
            [
                [np.cos(camera_rotation), -np.sin(camera_rotation)],
                [np.sin(camera_rotation), np.cos(camera_rotation)],
            ]
        )
        self._frame_width = cam_frame_width
        self._frame_height = cam_frame_height

    def get_path_snake(
        self,
        top_left: MatLike,
        bottom_right: MatLike,
        units: Units,
        overlap_h: float,
        overlap_v: float,
    ) -> Path:
        """
            Generate snaking path from top left to bottom right point where each path point overlaps
            with its neighbouring tiles by overlap_h and overlap_v percentage

            The path is a 2d list where each row of points is a horizontal row of the path
        Args:
            top_left (MatLike): top left corner of tiling region
            bottom_right (MatLike): bottom right corner of tiling region
            units (Units): units of measurement for top_left and bottom_right params (must be LENGTH)
            overlap_h (float): desired horizontal overlap between images (decimal percentage)
            overlap_v (float): desired vertical overlap between images (decimal percentage)
        """
        frame_width_um: float = self._pxl_w_um * self._frame_width
        frame_height_um: float = self._pxl_h_um * self._frame_height
        sample_area_width_um: float = convert_length_to_microns(
            bottom_right[0] - top_left[0], units
        )
        sample_area_height_um: float = convert_length_to_microns(
            top_left[1] - bottom_right[1], units
        )

        # get num steps and compute horizontal and vertical coverage
        step_x_um: float = (1.0 - overlap_h) * frame_width_um
        step_y_um: float = (1.0 - overlap_v) * frame_height_um
        steps_x, coverage_x = get_steps_and_coverage(step_x_um, sample_area_width_um)
        steps_y, coverage_y = get_steps_and_coverage(step_y_um, sample_area_height_um)

        TOP_LEFT_MICRONS = convert_length_to_microns(top_left, units)
        BOTTOM_RIGHT_MICRONS = convert_length_to_microns(bottom_right, units)
        x_left_um = TOP_LEFT_MICRONS[0] - (coverage_x - sample_area_width_um) / 2.0
        x_right_um = BOTTOM_RIGHT_MICRONS[0] + (coverage_x - sample_area_width_um) / 2.0
        y_top_um = TOP_LEFT_MICRONS[1] - (coverage_y - sample_area_height_um) / 2.0

        path: list[list[tuple[float, float]]] = []
        for y in range(steps_y):
            y_pos = y_top_um - y * step_y_um
            grid_row: list[tuple[float, float]] = []
            for x in range(steps_x):
                x_pos = 0.0
                if not y & 1:
                    x_pos = x_left_um + x * step_x_um
                else:
                    x_pos = x_right_um - x * step_x_um

                step_vec: NDArray = np.array([x_pos - x_left_um, 0.0])
                step_vec = self._rotation_matrix_2d @ step_vec
                grid_row.append((x_left_um + step_vec[0], y_pos + step_vec[1]))
            path.append(grid_row)
        return path


def get_steps_and_coverage(step_um: float, distance_um: float) -> tuple[int, float]:
    steps: int = int(np.floor(distance_um / step_um) + 1)
    coverage = (steps - 1) * step_um
    if coverage < distance_um:
        steps += 1
        coverage = (steps - 1) * step_um
    return steps, coverage

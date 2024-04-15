import cv2
import pypylon.pylon as py
from cv2.typing import MatLike

# binning params -- choose between "Sum" and "Average" binning modes
BINNING_HORIZONTAL: int = 1
BINNING_VERTICAL: int = 1
BINNING_MODE_HORIZONTAL: str = "Sum"
BINNING_MODE_VERTICAL: str = "Sum"

MAX_TIMEOUT_MS = 2000
MAX_ATTEMPTS = 20

class ImageCaptureError(RuntimeError):
    pass


class BaslerCameraWrapper:
    """
    Wrapper for Basler pylon InstantCamera class
    - More code examples using the pypylon library and InstantCamera API can be found here:
    https://github.com/basler/pypylon/tree/master/samples

    - WARNING: __init__ will hang if Basler Pylon application is open
    """

    def __init__(self, bin_h: int, bin_mode_h: str, bin_v: int, bin_mode_v: str):
        """
        BaslerCameraWrapper constructor
        - you may want to adjust settings depending on your camera and the lighting conditions
        it is operating in
        - you can copy any settings from the Basler Pylon application.
        """
        # TODO: add try-catch and error handling + output messages here
        self._tlf: py.TlFactory = py.TlFactory.GetInstance()
        self._cam: py.InstantCamera = py.InstantCamera(self._tlf.CreateFirstDevice())
        self._cam.Open()
        self._frame_width = self._cam.Width.Max
        self._frame_height = self._cam.Height.Max
        self._bin_h = bin_h
        self._bin_v = bin_v

        # Fields can be set using py.InstantCamera's node map
        # Field and enum value names are equivalent to those in the Basler Pylon application
        node_map = self._cam.GetNodeMap()
        node_map.Width.Value = self._frame_width
        node_map.Height.Value = self._frame_height
        node_map.CenterX.Value = True
        node_map.CenterY.Value = True
        node_map.PixelFormat.Value = "Mono8"
        node_map.Gain.Value = 10.0
        node_map.ExposureAuto.Value = "Continuous"
        node_map.ExposureMode.Value = "Timed"

        node_map.BinningHorizontal.Value = bin_h
        node_map.BinningHorizontalMode.Value = bin_mode_h
        node_map.BinningVertical.Value = bin_v
        node_map.BinningVerticalMode.Value = bin_mode_v
        print(
            "BaslerCameraWrapper: opened py.InstantCamera with framerate:",
            self._cam.ResultingFrameRate.Value,
        )

    def grab_frame(self) -> MatLike:
        """
            Capture and return latest frame from camera buffer:
            you may want to adjust colour conversion settings depending on your camera

        Returns:
            MatLike: 24-bit BGR image converted from camera grayscale
        """
        self._cam.StartGrabbing(1, py.GrabStrategy_LatestImageOnly)
        ret: MatLike = []
        num_attempts: int = 0
        while num_attempts < MAX_ATTEMPTS:
            with self._cam.RetrieveResult(MAX_TIMEOUT_MS) as result:
                if result.GrabSucceeded():
                    with result.GetArrayZeroCopy() as out_array:
                        ret = out_array
                        break

        if len(ret) == 0:
            raise ImageCaptureError("pylon.InstantCamera failed to capture image")

        self._cam.StopGrabbing()
        return cv2.cvtColor(ret, cv2.COLOR_GRAY2BGR)

    def get_frame_width(self) -> int:
        return self._frame_width

    def get_frame_height(self) -> int:
        return self._frame_height

    def get_binning_horizontal(self) -> int:
        return self._bin_h

    def get_binning_vertical(self) -> int:
        return self._bin_v

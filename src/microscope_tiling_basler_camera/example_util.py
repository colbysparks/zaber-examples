import cv2
from cv2.typing import MatLike
from zaber_motion import Units, Measurement


def convert_measurement_to_microns(m: Measurement) -> float:
    """
        Convert arbitrary measurement length to length in microns
    Args:
        m: measurement (units must be Length)

    Returns:
        float: _description_
    """
    return convert_length_to_microns(m.value, m.unit)


def convert_length_to_microns(length: float | MatLike, unit: Units) -> float | MatLike:
    """
        Convert number from specified unit of length to microns
    Args:
        length: numeric type (numpy arrays are ok)
        unit: unit of measurement for length param

    Returns:
        float or MatLike with each component converted to microns
    """

    match unit:
        case Units.LENGTH_METRES:
            return length * 10**9
        case Units.LENGTH_CENTIMETRES:
            return length * 10**6
        case Units.LENGTH_MILLIMETRES:
            return length * 10**3
        case Units.LENGTH_MICROMETRES:
            return length
        case Units.LENGTH_NANOMETRES:
            return length / 1000.0
        case Units.LENGTH_INCHES:
            return length * 25400.0

    print(
        "ERROR: convert_length_to_microns Measurement unit must be LENGTH, instead received ", unit
    )
    return length


def is_even(num: int):
    return not num & 1


def resize_image(img: MatLike, scale: float):
    return cv2.resize(img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


def try_stitch_images(tiles: list[list[MatLike]], num_rows: int, scale: float = 1.0) -> None:
    """
        Attempts to stitch tiled images row by row using openCV's high level stitching API
        - this function is not guaranteed to succeed, but in general the more overlap the better

    Args:
        tiles (list[list[MatLike]]): list of tile rows
        num_rows (int): number of tile rows
        scale (float): decimal percentage representing scale of final image
    """
    stitched_rows = []
    for i in range(num_rows):
        row = tiles[i]
        if scale < 1.0:
            row = map(row, lambda img: resize_image(img, scale))

        stitcher = cv2.Stitcher.create(cv2.Stitcher_SCANS)
        (status, stitched_row) = stitcher.stitch(row)

        if status == cv2.Stitcher_OK:
            stitched_rows.append(stitched_row)
            filename = "stitched_rows/row{0}.png".format(i)
            cv2.imwrite(filename, stitched_row)
        else:
            raise RuntimeError

    stitcher = cv2.Stitcher.create(cv2.Stitcher_SCANS)
    (status, stitched_final) = stitcher.stitch(stitched_rows)

    if status == cv2.Stitcher_OK:
        cv2.imwrite("stitched_rows_final.png", stitched_final)
    else:
        print("status not ok!")


def join_tiles(tiles: list[list[MatLike]], num_rows: int, scale: float = 1.0) -> None:
    """
        Joins tiles into single image
    Args:
        tiles (list[MatLike]): list of tile rows
        num_rows (int): number of tile rows
        scale (float): decimal percentage representing scale of final image
    """
    tiled_rows = []
    for i in range(num_rows):
        row = tiles[i]
        row_img: MatLike = row[0]
        if scale < 1.0:
            row_img = resize_image(row_img, scale)

        for i in range(1, len(row)):
            row_img = cv2.hconcat([row_img, row[i]])
        tiled_rows.append(row_img)

    final_img: MatLike = tiled_rows[0]
    for i in range(1, len(tiled_rows)):
        final_img = cv2.vconcat([final_img, tiled_rows[i]])
    cv2.imwrite("tiled_rows_final.png", final_img)

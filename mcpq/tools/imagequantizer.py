import os
from pathlib import Path as _Path


def konvertiere_bild(
    bild: _Path | os.PathLike | str,
    neuesFormat: tuple[int, int] | None = None,
    zeige: bool = False,
):
    """Nimmt ein Bild oder den Pfad eines Bildes entgegen und wandelt
    es in die 16 Minecraft Wollfarben um.

    Argumente:
        bild (str, list):
            Der Pfad zu einem PNG oder JPG Bild.
            Alternativ kann auch ein 2D Feld mit RGB Werten gegeben werden.
        neuesFormat (tuple(int, int), optional):
            Die Größe auf die das Bild geändert werden soll.
            zB. ein großes Bild kann kleiner gemacht werden.
        zeige (bool, optional):
            Ob das umgewandelte Bild zusätzlich geöffnet werden soll.

    Returns:
        Ein 2D Array, dessen Inhalt die Farbwerte 0 - 15 des umgewandelten Bildes sind.
    """
    try:
        import imageio
        import numpy
        import PIL
        import scipy
    except ImportError as exc:
        print("WARN: konvertiere_bild braucht zusätzliche Python Module!")
        print("Installiere sie mit: 'pip install numpy scipy imageio Pillow'")
        raise exc
    return convert_image(bild, neuesFormat, zeige)


# ---------------------------------------------------------
# Englische Definitionen
# ---------------------------------------------------------


def convert_image(
    image: _Path | os.PathLike | str, newsize: tuple[int, int] | None = None, show: bool = False
):
    try:
        import numpy as np
        import scipy.ndimage as nd
        from imageio import imread, imwrite
        from PIL import Image
    except ImportError as exc:
        print("WARN: Imagequantizer needs additional requirements!")
        print("Install with: 'pip install numpy scipy imageio Pillow'")
        raise exc
    if type(image) == str:
        # read image as array
        img = imread(image)
    elif type(image) == list:
        img = np.array(image)
    elif type(image) == np.ndarray:
        pass
    else:
        raise TypeError(
            f"Unknown type of image `{type(image)}`."
            "Should be `str` (filename), `list` or `np.ndarray`"
        )

    # resize if new size is given
    if newsize is not None:
        assert type(newsize) == tuple and len(newsize) == 2
        assert type(newsize[0]) == int and type(newsize[1]) == int
        assert newsize[0] > 0 and newsize[1] > 0
        img = np.array(Image.fromarray(img).resize(newsize))

    rgb_palette = np.array([list(c) for c in _RGB.values()])
    index_keys = np.array(list(_RGB.keys()))

    # quantize image file
    result, indices = quantize(img, rgb_palette)

    # show image
    if show:
        Image.fromarray(result).show()

    indices_to_keys = np.array([[index_keys[index] for index in row] for row in indices.T])

    return indices_to_keys


def quantize(img, palette):
    """
    quantize an image with a given color palette

    :param img: A numpy array of shape (height, width, 3)
                with RGB(A) values (alpha values will be ignored).
    :param palette: The x colors which should be used in the new image
                    in form of a numpy array of shape (x, 3).
    :returns: A tuple (res, idx) where res is the new image
              and idx are the indicies of the chosen colors of the palette.

    Adapted from https://gist.github.com/cuppster/4004895
    """

    import numpy as np
    from scipy.cluster.vq import vq

    # check if image has alpha and remove it
    if img.shape[2] == 4:
        img = np.delete(img, 3, 2)  # delete fourth "row" of depth in (RGB*A*)

    # reshape to array of points
    pixels = np.reshape(img, (img.shape[0] * img.shape[1], 3))

    # quantize
    qnt, _ = vq(pixels, palette)

    # reshape back to image
    centers_idx = np.reshape(qnt, (img.shape[0], img.shape[1]))

    # convert from indecies to colors
    clustered = palette[centers_idx]

    # make sure type of clustered is correct (RGB 0 - 255)
    clustered = clustered.astype(np.uint8)

    # return quantized image and quantized indecies
    return clustered, centers_idx


def _colorCodeToRGB(colorcode):
    """Convert a colorcode into a tuple with values between 0 and 255
    e.g. "00DDFF" -> (0, 221, 255)
    """
    assert len(colorcode) == 6 or len(colorcode) == 8
    return (int(colorcode[0:2], 16), int(colorcode[2:4], 16), int(colorcode[4:6], 16))


_RGB = {
    "white_wool": _colorCodeToRGB("E9ECEC"),
    "orange_wool": _colorCodeToRGB("F07613"),
    "magenta_wool": _colorCodeToRGB("BD44B3"),
    "light_blue_wool": _colorCodeToRGB("3AAFD9"),
    "yellow_wool": _colorCodeToRGB("F8C627"),
    "lime_wool": _colorCodeToRGB("70B919"),
    "pink_wool": _colorCodeToRGB("ED8DAC"),
    "gray_wool": _colorCodeToRGB("3E4447"),
    "light_gray_wool": _colorCodeToRGB("8E8E86"),
    "cyan_wool": _colorCodeToRGB("158991"),
    "purple_wool": _colorCodeToRGB("792AAC"),
    "blue_wool": _colorCodeToRGB("35399D"),
    "brown_wool": _colorCodeToRGB("724728"),
    "green_wool": _colorCodeToRGB("546D1B"),
    "red_wool": _colorCodeToRGB("A12722"),
    "black_wool": _colorCodeToRGB("141519"),
}

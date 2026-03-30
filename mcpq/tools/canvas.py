from __future__ import annotations

import os
import textwrap
from contextlib import contextmanager
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as ImageType
from PIL.ImageFont import FreeTypeFont

from .. import Block, Minecraft, Vec3, World


def _colorCodeToRGB(colorcode):
    """Convert a colorcode into a tuple with values between 0 and 255
    e.g. "00DDFF" -> (0, 221, 255)
    """
    assert len(colorcode) == 6 or len(colorcode) == 8
    return (int(colorcode[0:2], 16), int(colorcode[2:4], 16), int(colorcode[4:6], 16))


_PALETTE_RGB_WOOL = {
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


class Canvas:
    def __init__(self, world: Minecraft | World) -> None:
        self._world: Minecraft | World = world
        self._blocktype: Block = Block("black_wool")
        self._palette: dict[str, tuple[int, int, int]] = _PALETTE_RGB_WOOL
        self._font_path: Path | None = None
        self._font_size: int = 10
        self._ifont: ImageFont.FreeTypeFont | None = None
        self._image: ImageType | None = None
        self._image_original: ImageType | None = None
        self._start: Vec3 | None = None
        self._dir_w: Vec3 | None = None
        self._dir_h: Vec3 | None = None
        self._w: int = 0
        self._h: int = 0

    @classmethod
    def create_at(cls, start: Vec3, end: Vec3, flip_dir: bool = False):
        ...

    @classmethod
    def create_at(cls, start: Vec3, width: int, height: int, flip_dir: bool = False):
        ...

    @property
    def is_positioned(self) -> bool:
        return self._start and self._dir_w and self._dir_h and self._w and self._h

    @property
    def _end(self) -> Vec3:
        return self._start + self._dir_w * self._w + self._dir_h * self._h

    def load_image(
        self,
        image_path: str | os.PathLike[str] | Path | None = None,
        show: bool = False,
    ):
        if image_path is None:
            image_path = Path(__file__).parent / "assets" / "ara.jpg"
            if not self._w or not self._h:
                self.resize(128, 85)  # resize ara.jpg
        self._image_original = Image.open(image_path)
        if self._w and self._h:
            self._image = self._image_original.resize((self._w, self._h))
        else:
            self._image = self._image_original.copy()  # also loads image
            self._w, self._h = self._image.width, self._image.height
        self._quantize()
        if show:
            self._image.show()
        return self

    def resize(
        self,
        width: int | None = None,
        height: int | None = None,
        *,
        keep_oob: bool = False,
    ):
        if width and width > 0:
            self._w = width
        if height and height > 0:
            self._h = height
        if self._image and (self._image.width != self._w or self._image.height != self._h):
            self._image = self._image_original.resize((self._w, self._h))
            self._quantize()
        return self

    def _quantize(self, dither: bool = False):
        assert self._image is not None
        num_colors = len(self._palette)
        if num_colors < 2:
            raise ValueError(f"Need at least 2 colors for quantization, got {num_colors}")
        if num_colors > 256:
            raise ValueError(
                f"Does only support quantization up to 256 colors (for now), got {num_colors}"
            )
        palette_list = list(self._palette.values())
        palette_list_flat = [color for rgb in palette_list for color in rgb]
        palette_img = Image.new("P", (1, 1))
        palette_img.putpalette(palette_list_flat)
        self._image = self._image.convert("RGB")
        if dither:
            self._image = self._image.quantize(palette=palette_img)
        else:
            self._image = self._image.quantize(palette=palette_img, dither=Image.Dither.NONE)

    def draw_image(self, by_color: bool = False, wait_time: float = 0):
        assert self._image is not None
        assert self._image.mode == "P"
        assert self._start
        assert self._dir_w
        assert self._dir_h
        palette = list(self._palette.keys())
        assert isinstance(
            self._image.getpixel((0, 0)), int
        ), f"Wrong image content type, expected int was {type(self._image.getpixel((0 ,0)))}"
        if not by_color:
            for i in range(self._w):
                for j in range(self._h):
                    index = self._image.getpixel((i, j))
                    color = palette[index]
                    pos = self._start + (self._dir_w * i) + (self._dir_h * j)
                    self._world.setBlock(color, pos)
                    if wait_time > 0:
                        time.sleep(wait_time)
        else:
            color_blocks: dict[str, list[Vec3]] = {color: [] for color in palette}
            for i in range(self._w):
                for j in range(self._h):
                    index = self._image.getpixel((i, j))
                    color = palette[index]
                    pos = self._start + (self._dir_w * i) + (self._dir_h * j)
                    color_blocks[color].append(pos)
            for color, blocks in color_blocks.items():
                self._world.setBlockList(color, blocks)
                if wait_time > 0:
                    time.sleep(wait_time)

    def load_font(
        self,
        font_path: str | os.PathLike[str] | Path | None = None,
        font_size: int | None = None,
        show: bool = False,
    ):
        if font_path is None:
            font_path: Path = Path(__file__).parent / "assets" / "monogram.ttf"
        font_path = Path(font_path)
        if not font_path.exists():
            raise FileNotFoundError(f"Font was not found at path: {font_path.as_posix()}")
        if font_path.is_dir():
            raise TypeError(
                f"Font path is a directory, not a file at path: {font_path.as_posix()}"
            )
        if font_size and font_size > 0:
            self._font_size = font_size
        self._ifont = ImageFont.truetype(font_path, self._font_size)
        self._font_path = font_path
        if show:
            raise NotImplementedError
        return self

    def at(self, start: Vec3, end: Vec3, flipside: bool = False):
        """When positioning with start and end
        * if the image is standing, the front will always be along the x/z axis (in writing direction)
        * if the image is laying, the front will always be up (positive y axis)
        If flipside is True, these two are exactly reversed
        """
        start, end = start.floor(), end.floor()
        diff = end - start
        if diff == Vec3():
            raise ValueError(
                "Start and end must span a plane, not a point (two coordinate must be different)"
            )
        if diff.x and diff.y and diff.z:
            raise ValueError(
                "Start and end must span a plane, not a cube (one coordinate must be the same)"
            )
        if (
            (diff.x and not diff.y and not diff.z)
            or (not diff.x and diff.y and not diff.z)
            or (not diff.x and not diff.y and diff.z)
        ):
            raise ValueError(
                "Start and end must span a plane, not a line (two coordinate must be different)"
            )

        if diff.y:  # standing canvas
            assert diff.x == 0 or diff.z == 0
            along = Vec3(diff.x, 0, diff.z)
            down = Vec3(0, diff.y, 0)
        else:  # laying canvas
            if (diff.x > 0 and diff.z > 0) or (diff.x < 0 and diff.z < 0):
                along = Vec3(diff.x, 0, 0)
                down = Vec3(0, 0, diff.z)
            else:
                along = Vec3(0, 0, diff.z)
                down = Vec3(diff.x, 0, 0)

        if flipside:
            along, down = down, along

        self._start = start
        self._dir_w = along.norm()
        self._dir_h = down.norm()
        self._w = round(along.length())
        self._h = round(down.length())
        assert (
            self._start + self._dir_w * self._w + self._dir_h * self._h == end
        ), f"{self._start + self._dir_w * self._w + self._dir_h * self._h} == {end}"
        # self._end = end
        # self._along = along

    @property
    @contextmanager
    def _draw_buffer(self, show: bool = False):
        if not self.is_positioned:
            raise RuntimeError(
                "Canvas has to be positioned in the world first, use canvas.at(...)"
            )

        start: Vec3 = self._start
        along: Vec3 = self._dir_w
        write_down: Vec3 = self._dir_h
        # end, along =, self._end, self._along
        # diff = end - start
        # write_down = (diff - along).norm()
        # along = along.norm()
        assert along == along.closest_axis()
        assert write_down == write_down.closest_axis()

        with Image.new("1", (self._w, self._h), color=0) as img:
            draw = ImageDraw.Draw(img)
            yield draw
            # draw.text((offx, offy), text, font=font, fill=(255,))
            if show:
                img.show()
            # if dry_run:
            #     return
            data = list(img.getdata())

        blocks = []
        for index, pixel in enumerate(data):
            if pixel:
                dx, dy = index % self._w, index // self._w
                vpos = start + along * dx + write_down * dy
                blocks.append(vpos)

        self._world.setBlockList(self._blocktype, blocks)

    def clear(self):
        # TODO: save text, render later?
        if self.is_positioned:
            self._world.setBlockCube("air", self._start, self._end)
        else:
            raise RuntimeError(
                "Canvas has to be positioned in the world first before it can be cleared, use canvas.at(...)"
            )

    def text(self, text, pos: tuple[int, int] = (0, 0)):
        if self._ifont is None:
            self.load_font()
        offx, offy = pos
        with self._draw_buffer as draw:
            draw.text((offx, offy), text, font=self._ifont, fill=(255,))
        return self

    def text_wrap(
        self,
        text,
        pos: tuple[int, int] = (0, 0),
        spacing: int | None = None,
        relative_spacing: float | None = None,
    ):
        if self._ifont is None:
            self.load_font()

        font: FreeTypeFont = self._ifont
        (text_w, baseline), (offset_x, offset_y) = font.font.getsize(text)
        letter_w = text_w / len(text)  # TODO: works only for mono-font
        lines = textwrap.wrap(text, width=int(self._w / letter_w))
        self.text_lines(
            lines,
            pos=pos,
            spacing=spacing,
            relative_spacing=relative_spacing,
        )
        return self

    def text_lines(
        self,
        lines: list[str],
        pos: tuple[int, int] = (0, 0),
        spacing: int | None = None,
        relative_spacing: float | None = None,
    ):
        if self._ifont is None:
            self.load_font()

        if spacing is None:
            if relative_spacing is None:
                spacing = 4 + self._font_size
            else:
                spacing = int(relative_spacing * self._font_size)
        else:
            spacing += self._font_size
        offx, offy = pos
        with self._draw_buffer as draw:
            for line in lines:
                draw.text((offx, offy), line, font=self._ifont, fill=(255,))
                offy += spacing
        return self


if __name__ == "__main__":
    import time

    mc = Minecraft()
    c = Canvas(mc)
    p = mc.getPlayer()
    w, h = 60, 40
    center = (p.pos + p.facing.norm() * 60).floor()
    front_dir = (p.pos - center).withY(0).closest_axis()
    assert front_dir
    up = Vec3.UP
    left = front_dir.cross(up).norm()
    upper_left = center + left * w // 2 + up * h // 2
    lower_right = center - left * w // 2 - up * h // 2
    c.at(upper_left, lower_right)
    c.load_image()  # default: ara.jpg
    c.draw_image(True)
    c.load_font(None, 16)
    print("DONE DRAWING")
    mc.setBlock("diamond_block", upper_left)
    mc.setBlock("emerald_block", lower_right)
    time.sleep(1)
    c._blocktype = "redstone_block"
    c.text_wrap(
        "This is a long text and I dont know how long I will write, definitly long enough to get at least two wrap-arounds. However, this is tedious, I wish I had the lorem ipsum package installed, lol"
    )
    time.sleep(2)
    try:
        while True:
            c.clear()
            c.text(time.strftime("%H:%M:%S"))
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    c.clear()

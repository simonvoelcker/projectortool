# Projector tool

A simple script to convert back and forth between panoramic pictures in different projection.

The supported projections are:
- Equi-rectangular projection (ideal aspect ratio 2:1)
- Cube map projection (ideal aspect ratio 4:3)
- Hemispherical projection (ideal aspect ratio 1:1)

![Example](example.jpg?raw=true "Example")

## Dependencies

- Python3.7
- Pillow

## Usage

`python project.py <input image> --in-projection <projection> --out-projection <projection> [--out <output image> --width <int> --height <int>]`

*projection* is one of "equirectangular", "cubemap", "hemispherical".

Example:

`python project.py example_equi.jpg --in-projection equirectangular --out-projection cubemap`

- support az/alt offsets
- make hemi fov configurable
- support super sampling
- fix off by one shit
- beautiful readme
- automatic detection of source projection
- automatic output file size (retain height or width, whichever is ~lossless)
- automatic output file name (projection suffix)
- tests

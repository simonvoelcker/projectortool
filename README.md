# Projector tool

Scripts to convert back end forth between panoramic pictures in different projection. Input and output are simple pictures.

The supported projections are:
- Equi-rectangular projection (ideal aspect ratio 2:1)
- Cube map projection (ideal aspect ratio 4:3)
- Work in progress: Hemispherical projection (ideal aspect ration 1:1)

![Example](example.jpg?raw=true "Example")

## Dependencies

- Python3.7
- Pillow

## Usage

`python project.py <input image> --in-projection <projection> --out-projection <projection> [--out <output image> --width <int> --height <int>]`

*projection* is one of "equirectangular", "cubemap", "hemisperical".

Example:

`python project.py example_equi.jpg --in-projection equirectangular --out-projection cubemap`

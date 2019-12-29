# Projector tool

Scripts to convert back end forth between panoramic pictures in different projection. Supported are equi-rectangular projection and cube maps, each given as a simple picture. The equi-rectangular pictures should ideally have 2:1 aspect ratio, the cube maps 4:3.

## Dependencies

- Python3.7 
- Pillow

## Usage

In both scripts, the input image is the only required argument. Use --samples with care, its time-complexity grows with the square of the argument.

### Equi-rectangular to cube map

`python equi2cube.py <input image> [--out <output image> --face-size <size> --samples <samples>]`

### Cube map to equi-rectangular

`python cube2equi.py <input image> [--out <output image> --height <height> --samples <samples>]`

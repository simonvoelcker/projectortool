# Projector tool

A simple script to convert back and forth between panoramic pictures in different projections.

## Supported projections

### Equi-rectangular projection
Popular for use cases where the image quality matters most along the equator and less at the poles. The ideal aspect ratio is 2:1.
![Equi-rectangular image](example_equi.jpg?raw=true "Equi-rectangular image")

### Cube map projection
Often used in games because it is easy to render. Distortions are highest near the edges and corners. The ideal aspect ratio is 4:3.
![Cube map image](example_cube.jpg?raw=true "Cube map image")

### Hemispherical projection
Produced by wide-angle (fish eye) lenses. Distortion drastically increases towards the edges. The ideal aspect ratio is 1:1.
![Hemispherical image](example_hemi.jpg?raw=true "Hemispherical image")

## Dependencies

- Python 3.7 or greater. f-strings and type hints are used.
- Pillow
- Numpy

## Usage

`python project.py <input image> --in-projection <projection> --out-projection <projection> --out <output image> --width <int> --height <int> --samples <int> --rotation <int,int,int> --hemi-fov-x <int> --hemi-fov-y <int>`

- **--in-projection** can be any of **equirectangular**, **cubemap**, **hemispherical**. Can also be left blank for auto detection based on aspect ratio.
- **--width** and **--height** control the size of the output image. If omitted, a reasonable size is picked based on input image size and output projection.
- **--samples** can be used to specify super-sampling quality. N times N samples per pixel will be taken, so this has a serious performance penalty.
- **--rotation** allows for a rotation of the scene along the x, y and z axes. The rotation is applied in this order and must be specified as comma-separated integers (degrees).
- **--hemi-fov-x** and **--hemi-fov-y** can be used to specify the field of view along the x and y image axes when using hemispherical projection. If your image is not square but the scene is circular as in the example image above, the ratio of the FOVs should match the aspect ratio of the image. In the example image, the correct FOVs are x=180 and y=121.

Example:

`python project.py example_equi.jpg --in-projection equirectangular --out-projection cubemap --out cube.png --width 1536 --height 1024 --samples 2 --rotation 180,90,0`

## Bulk processing

To process a large number of images with the same parameters, use the `project_many.py` script. It generates a lookup table for the projection parameters and given image resolution, which can be applied quickly to many images. Instead of an image file path, it accepts a path to a text file which in turn should contain image file paths. Specify the output directory using `--out-dir`. The `--samples` parameter is not supported in this case.

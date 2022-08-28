import sys
import argparse
from typing import Tuple

from PIL import Image
from projections.base import Point
from projections.cubemap import CubemapProjection
from projections.equirectangular import EquirectangularProjection
from projections.hemispherical import HemisphericalProjection

projections = {
    'cubemap': CubemapProjection,
    'equirectangular': EquirectangularProjection,
    'hemispherical': HemisphericalProjection,
}


parser = argparse.ArgumentParser()
parser.add_argument('image', type=str, help='Input image file')
parser.add_argument('--in-projection', type=str, default='auto', help=f'Input image projection. One of {projections.keys()}')
parser.add_argument('--out', type=str, default='out.jpg', help='Output file name')
parser.add_argument('--out-projection', type=str, help=f'Output image projection. One of {projections.keys()}')
parser.add_argument('--width', type=int, help='Width of output image, in pixels')
parser.add_argument('--height', type=int, help='Height of output image, in pixels')
parser.add_argument('--rotation', type=str, help='Rotate by given angles (<x>,<y>,<z> in degrees)')
parser.add_argument('--samples', type=int, default=1, help='Take NxN samples per pixel. Caution: Slow.')
parser.add_argument('--hemi-fov-x', type=int, default=180, help='Horizontal field of view (in degrees) of hemispherical projection')
parser.add_argument('--hemi-fov-y', type=int, default=180, help='Vertical field of view (in degrees) of hemispherical projection')

args = parser.parse_args()

input_image = Image.open(args.image)

in_projection = args.in_projection
in_width, in_height = input_image.size
in_aspect_ratio = float(in_width) / float(in_height)
if in_projection == 'auto':
    # Detect input projection based on image aspect ratio
    for projection_name, projection_class in projections.items():
        if projection_class.aspect_ratio() == in_aspect_ratio:
            in_projection = projection_name
    # No match found, ask the user to specify projection
    if in_projection == 'auto':
        print('Specify input projection using --in-projection')
        sys.exit(0)

projection_kwargs = {
    'hemi_fov_x': args.hemi_fov_x,
    'hemi_fov_y': args.hemi_fov_y,
}

input_projection = projections[in_projection](**projection_kwargs)
output_projection = projections[args.out_projection](**projection_kwargs)

out_width, out_height = args.width, args.height
if not out_width or not out_height:
    # Come up with reasonable output image size based on
    # input image size and desired output projection
    out_aspect_ratio = output_projection.aspect_ratio()
    if out_width:
        out_height = int(out_width / out_aspect_ratio)
    elif out_height:
        out_width = int(out_height * out_aspect_ratio)
    else:
        out_width = in_width
        out_height = int(out_width / out_aspect_ratio)

output_image = Image.new('RGB', (out_width, out_height), 'black')


def sample_input_image(point: Point) -> Tuple[int, int, int]:
    direction = output_projection.to_direction(point)
    if not direction:
        # Projection gaps may exist -> Return black
        return 0, 0, 0
    if args.rotation:
        angle_x, angle_y, angle_z = args.rotation.split(',')
        direction = direction.rotated(int(angle_x), int(angle_y), int(angle_z))
    input_point = input_projection.to_point(direction)
    if not input_point:
        return 0, 0, 0
    return input_image.getpixel((
        int(input_point.x * (input_image.size[0] - 1)),
        int(input_point.y * (input_image.size[1] - 1))
    ))


total_samples = args.samples * args.samples


def get_sample(out_x, out_y):
    if args.samples == 1:
        # One sample per pixel
        output_point = Point(
            out_x / out_width,
            out_y / out_height
        )
        return sample_input_image(output_point)
    else:
        # Super-sampling (slow, even if args.samples==1)
        r, g, b = 0, 0, 0
        for y_sample in range(args.samples):
            for x_sample in range(args.samples):
                output_point = Point(
                    (out_x + x_sample/args.samples) / out_width,
                    (out_y + y_sample/args.samples) / out_height
                )
                sample = sample_input_image(output_point)
                r += sample[0]
                g += sample[1]
                b += sample[2]
        return r // total_samples, g // total_samples, b // total_samples


# Render image
for y in range(out_height):
    for x in range(out_width):
        output_image.putpixel((x, y), get_sample(x, y))

output_image.save(args.out)

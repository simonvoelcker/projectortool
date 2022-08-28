import sys
import argparse

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

input_projection = projections[in_projection]()
output_projection = projections[args.out_projection]()

out_width, out_height = args.width, args.height
if not out_width or not out_height:
    # Come up with reasonable output image size based on
    # input image size and desired output projection
    out_aspect_ratio = output_projection.aspect_ratio()
    if not out_width:
        out_width = in_width
        out_height = int(out_width / out_aspect_ratio)
    if not out_height:
        out_height = in_height
        out_width = int(out_height * out_aspect_ratio)

output_image = Image.new('RGB', (out_width, out_height), 'black')

# Render image
for y in range(out_height):
    for x in range(out_width):
        output_point = Point(x/out_width, y/out_height)
        direction = output_projection.to_direction(output_point)
        if not direction:
            # Projection gaps may exist. Pixel keeps background color
            continue
        if args.rotation:
            angle_x, angle_y, angle_z = args.rotation.split(',')
            direction.rotate(int(angle_x), int(angle_y), int(angle_z))
        input_point = input_projection.to_point(direction)
        if not input_point:
            continue
        sample = input_image.getpixel((
            int(input_point.x * (input_image.size[0]-1)),
            int(input_point.y * (input_image.size[1]-1))
        ))
        output_image.putpixel((x, y), sample)

output_image.save(args.out)

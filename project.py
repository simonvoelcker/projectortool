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
parser.add_argument('--out', type=str, default='out.jpg', help='Output file')
parser.add_argument('--out-projection', type=str, help=f'Output image projection. One of {projections.keys()}')
parser.add_argument('--width', type=int, default=1024, help='Width of output image, in pixels')
parser.add_argument('--height', type=int, default=1024, help='Height of output image, in pixels')
parser.add_argument('--rotation', type=str, help='Rotate by given angles (<x>,<y>,<z> in degrees)')


args = parser.parse_args()

input_image = Image.open(args.image)

in_projection = args.in_projection
if in_projection == 'auto':
    # Detect input projection based on image aspect ratio
    width, height = input_image.size
    if width == height:
        in_projection = 'hemispherical'
    elif width == 2 * height:
        in_projection = 'equirectangular'
    elif 4 * height == 3 * width:
        in_projection = 'cubemap'
    else:
        print('Specify input projection using --in-projection')
        sys.exit(0)

input_projection = projections[in_projection]()
output_image = Image.new('RGB', (args.width, args.height), 'black')
output_projection = projections[args.out_projection]()

# Render image
for y in range(args.height):
    for x in range(args.width):
        output_point = Point(x/args.width, y/args.height)
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

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
parser.add_argument('--in-projection', type=str, help=f'Input image projection. One of {projections.keys()}')
parser.add_argument('--out', type=str, default='out.jpg', help='Output file')
parser.add_argument('--out-projection', type=str, help=f'Output image projection. One of {projections.keys()}')
parser.add_argument('--width', type=int, default=1024, help='Width of output image, in pixels')
parser.add_argument('--height', type=int, default=1024, help='Height of output image, in pixels')

args = parser.parse_args()

input_image = Image.open(args.image)
input_projection = projections[args.in_projection]()
output_image = Image.new('RGB', (args.width, args.height), 'black')
output_projection = projections[args.out_projection]()

# Render image
for y in range(args.height):
    for x in range(args.width):
        output_point = Point(x/args.width, y/args.height)
        angles = output_projection.to_angles(output_point)
        if not angles:
            # Projection gaps may exist. Pixel keeps background color
            continue
        input_point = input_projection.to_point(angles)
        if not input_point:
            continue
        sample = input_image.getpixel((
            int(input_point.x * (input_image.size[0]-1)),
            int(input_point.y * (input_image.size[1]-1))
        ))
        output_image.putpixel((x, y), sample)

output_image.save(args.out)

import argparse
from settings import Settings
from sampler import Sampler

from PIL import Image
from projections.map import projections_map


parser = argparse.ArgumentParser()
parser.add_argument('image', type=str, help='Input image file')
parser.add_argument('--in-projection', type=str, default='auto', help=f'Input image projection. One of {projections_map.keys()}')
parser.add_argument('--out', type=str, default='out.jpg', help='Output file name')
parser.add_argument('--out-projection', type=str, help=f'Output image projection. One of {projections_map.keys()}')
parser.add_argument('--width', type=int, help='Width of output image, in pixels')
parser.add_argument('--height', type=int, help='Height of output image, in pixels')
parser.add_argument('--rotation', type=str, help='Rotate by given angles (<x>,<y>,<z> in degrees)')
parser.add_argument('--samples', type=int, default=1, help='Take NxN samples per pixel. Caution: Slow.')
parser.add_argument('--hemi-fov-x', type=int, default=180, help='Horizontal field of view (in degrees) of hemispherical projection')
parser.add_argument('--hemi-fov-y', type=int, default=180, help='Vertical field of view (in degrees) of hemispherical projection')

args = parser.parse_args()
input_image = Image.open(args.image)
settings = Settings(args, input_image)

sampler = Sampler(args, settings, lambda px, py: input_image.getpixel((px, py)))

output_image = Image.new('RGB', (settings.out_width, settings.out_height), 'black')

# Render image
for y in range(settings.out_height):
    for x in range(settings.out_width):
        output_image.putpixel((x, y), sampler.get_supersample(x, y))

output_image.save(args.out)

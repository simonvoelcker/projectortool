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
input_image = Image.open(args.image).convert('RGB')
settings = Settings(args, input_image)
sampler = Sampler(args, settings, lambda in_x, in_y: input_image.getpixel((in_x, in_y)))
output_image = Image.new('RGB', (settings.out_width, settings.out_height), 'black')

# Render image
for out_y in range(settings.out_height):
    for out_x in range(settings.out_width):
        sample = sampler.get_supersample(out_x, out_y, args.samples)
        output_image.putpixel((out_x, out_y), sample)

output_image.save(args.out, quality=90)

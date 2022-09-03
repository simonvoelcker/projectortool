import argparse
import os
import numpy as np
from settings import Settings
from sampler import Sampler

from PIL import Image
from projections.map import projections_map


parser = argparse.ArgumentParser()
parser.add_argument('image_list', type=str, help='Input image file')
parser.add_argument('--in-projection', type=str, default='auto', help=f'Input image projection. One of {projections_map.keys()}')
parser.add_argument('--out-projection', type=str, help=f'Output image projection. One of {projections_map.keys()}')
parser.add_argument('--out-directory', type=str, default='out')
parser.add_argument('--width', type=int, help='Width of output image, in pixels')
parser.add_argument('--height', type=int, help='Height of output image, in pixels')
parser.add_argument('--rotation', type=str, help='Rotate by given angles (<x>,<y>,<z> in degrees)')
parser.add_argument('--hemi-fov-x', type=int, default=180, help='Horizontal field of view (in degrees) of hemispherical projection')
parser.add_argument('--hemi-fov-y', type=int, default=180, help='Vertical field of view (in degrees) of hemispherical projection')

args = parser.parse_args()
os.makedirs(args.out_directory, exist_ok=True)

with open(args.image_list) as f:
    image_path_list = f.readlines()

first_image = Image.open(image_path_list[0].strip())
settings = Settings(args, first_image)

print("Computing projection lookup table")
sample_recording = np.zeros((
    settings.out_width,
    settings.out_height,
    2,
), dtype=np.int16)


def record_sample(in_x, in_y):
    sample_recording[out_x, out_y, :] = [in_x, in_y]
    return 0, 0, 0


recording_sampler = Sampler(args, settings, record_sample)

# Run recording
for out_y in range(settings.out_height):
    for out_x in range(settings.out_width):
        recording_sampler.get_supersample(out_x, out_y)

# Render output images, looking up the coordinates from the recording
for image_index, image_path in enumerate(image_path_list):
    print(f"Processing file {image_index+1}/{len(image_path_list)}")

    input_image = Image.open(image_path.strip())
    input_image_buffer = np.asarray(input_image)
    input_image_buffer = np.swapaxes(input_image_buffer, 0, 1)

    if input_image_buffer.ndim == 2:
        input_image_buffer = np.expand_dims(input_image_buffer, 2)

    output_image_buffer = np.zeros((
        settings.out_width,
        settings.out_height,
        3
    ), dtype=np.uint8)

    for out_y in range(settings.out_height):
        for out_x in range(settings.out_width):
            in_x, in_y = sample_recording[out_x, out_y, :]
            sample = input_image_buffer[in_x, in_y, :]
            output_image_buffer[out_x, out_y, :] = sample

    output_image_buffer = np.swapaxes(output_image_buffer, 0, 1)
    output_image = Image.fromarray(output_image_buffer)
    output_file_path = os.path.join(
        args.out_directory,
        f"frame_{image_index:04d}.jpg",
    )
    output_image.save(output_file_path, quality=90)

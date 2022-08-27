import argparse

from PIL import Image
from projection import *


def get_sample(xy, img_equi_size, face_size, img_faces):
	angles = angles_from_img_xy(xy, img_equi_size)
	direction = direction_from_angles(angles)
	face, face_xy = face_and_face_xy_from_direction(direction, face_size)
	faces_xy = to_faces_xy(face_xy, face, face_size)
	sample = img_faces.getpixel(faces_xy)
	return sample


def get_multisample(xy, img_equi_size, face_size, img_faces, samples):
	r, g, b = 0, 0, 0
	for sx in range(samples):
		for sy in range(samples):
			sample_xy = (
				float(xy[0]) + float(sx) / float(samples),
				float(xy[1]) + float(sy) / float(samples)
			)
			sample = get_sample(sample_xy, img_equi_size, face_size, img_faces)
			r += sample[0]
			g += sample[1]
			b += sample[2]
	return (
		r // (samples*samples),
		g // (samples*samples),
		b // (samples*samples)
	)


def render_equi(img_faces, img_equi, face_size, samples):
	for y in range(img_equi.size[1]):
		if y % 100 == 0:
			print(f'{100*y/img_equi.size[1]} percent rendered')
		for x in range(img_equi.size[0]):
			multisample = get_multisample((x, y), img_equi.size, face_size, img_faces, samples)
			img_equi.putpixel((x, y), multisample)


def cube_to_equi(faces_img_path, equi_img_path, equi_size, samples):
	faces_img = Image.open(faces_img_path)
	face_size = (faces_img.size[0]/4, faces_img.size[1]/3)
	equi_img = Image.new('RGB', equi_size, 'black')
	render_equi(faces_img, equi_img, face_size, samples)
	equi_img.save(equi_img_path)


parser = argparse.ArgumentParser()
parser.add_argument('image', type=str, help='Input image file (cube map)')
parser.add_argument('--out', type=str, default='equi.jpg', help='Output file')
parser.add_argument('--height', type=int, default=1024, help='Height of output image, in pixels')
parser.add_argument('--samples', type=int, default=1, help='Use NxN samples per output pixel')

args = parser.parse_args()

cube_to_equi(args.image, args.out, (2*args.height, args.height), args.samples)
print('Done')

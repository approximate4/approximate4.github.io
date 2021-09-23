import imageio
import requests
import time
import config
import numpy as np
import os
from numpy.fft import fft2, ifft2, fftshift, ifftshift
from skimage.transform import resize
from skimage.filters import unsharp_mask


def process_image(filename, imagename):
	time.sleep(0.05)
	
	print("Processing: " + imagename)

	# Process with waifu2x
	r = requests.post(
		"https://api.deepai.org/api/waifu2x",
		files={
			'image': open(filename, 'rb'),
		},
		headers={'api-key': config.TOKEN}
	)
	output_url = r.json()['output_url']
	im = imageio.imread(output_url)

	# Read in filter image
	filterimage = np.copy(imageio.imread("./filterimagenew.png"))

	# Resize filter to shape of input image
	filterimage = resize(filterimage, [im.shape[0], im.shape[1]], anti_aliasing=True, mode="edge")

	# Initialise arrays
	im_filtered = np.zeros(im.shape, dtype=np.complex_)
	im_recon = np.zeros(im.shape, dtype=np.float_)

	# Apply filter to each RGB channel individually
	for i in range(0, 3):
		im_filtered[:, :, i] = np.multiply(fftshift(fft2(im[:, :, i])), filterimage)
		im_recon[:, :, i] = ifft2(ifftshift(im_filtered[:, :, i])).real

	# Scale between 0 and 255 for uint8
	minval = np.min(im_recon)
	maxval = np.max(im_recon)
	im_recon_sc = (255 * ((im_recon - minval) / (maxval - minval))).astype(np.uint8)

	# Borderify image
	pad = 57  # Pad image by 1/8th of inch on each edge
	bordertol = 16  # Overfill onto existing border by 16px
	im_padded = np.zeros([im.shape[0] + 2 * pad, im.shape[1] + 2 * pad, 3])

	# Set border colour
	bordercolour = [0,0,0]
		
	# Pad image
	for i in range(0, 3):
		im_padded[pad:im.shape[0] + pad, pad:im.shape[1] + pad, i] = im_recon_sc[:, :, i]

	# Overfill onto existing border
	# Left
	im_padded[0:im_padded.shape[0],
			  0:pad + bordertol, :] = bordercolour

	# Right
	im_padded[0:im_padded.shape[0],
			  im_padded.shape[1] - (pad + bordertol):im_padded.shape[1], :] = bordercolour

	# Top
	im_padded[0:pad + bordertol,
			  0:im_padded.shape[1], :] = bordercolour

	# Bottom
	im_padded[im_padded.shape[0] - (pad + bordertol):im_padded.shape[0],
			  0:im_padded.shape[1], :] = bordercolour
			  
	im_sharp = unsharp_mask(im_padded.astype(np.uint8), radius=3, amount=0.3)
	im_sharp = im_sharp * 255
			
	# Write image to disk
	imageio.imwrite("formatted/" + imagename + ".png", im_sharp.astype(np.uint8))


if __name__ == "__main__":
	# Loop through each image in images_local.txt and scan em all
	with open('images_local.txt', 'r') as fp:
		for filename in fp:
			filename = filename.rstrip()
			pipe_idx = filename.index("|")
			process_image(filename[0:pipe_idx], filename[pipe_idx+1:])
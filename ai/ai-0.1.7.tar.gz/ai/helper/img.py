# -*- coding: utf-8 -*-
""" ai.helper.img """
import os
import cv2
import numpy as np
from base64 import b64encode
from PIL import Image, ImageFont, ImageDraw
from ai.helper import ensure_dir


def imshow(img_path):
	img = cv2.imread(img_path)  
	cv2.imshow("Image", img)  
	cv2.waitKey(0)


def im2base64(img_path):
	with open(img_path, 'rb') as f:
	    tmp = b64encode(f.read())
	    s = tmp.decode()
	    return s


def frame2base64(img_np, fmt='.png'):
    img = cv2.imencode(fmt, img_np)[1]
    s = str(b64encode(img))[2:-1]
    return s


def imcompose(imgs, save_path='compose.png', width=256, height=256):
	assert len(imgs) >= 1, "The imgs can't be none!"
	row, col = len(imgs), len(imgs[0])
	target = Image.new('RGB', (col * width, row * height))
	for i, img_row in enumerate(imgs):
		for j, img in enumerate(img_row):
			tmp = Image.open(img).resize((width, height), Image.ANTIALIAS)
			target.paste(tmp, (j * width, i * height))
	ensure_dir(save_path)
	return target.save(save_path)


def imresize(img_path, save_dir='.', size=(256, 256)):
	name = img_path.rsplit('/', 1)[-1]
	im = Image.open(img_path).resize(size, Image.ANTIALIAS)
	ensure_dir(save_dir)
	im.save(f'{save_dir}/{name}')


def video2img(infile, save_dir=None):
	if not save_dir:
		save_dir = infile.rsplit('.', 1)[0]
	try:
		vc = cv2.VideoCapture(infile)
		rval = vc.isOpened()
	except:
		print("Cant load", infile)
		return
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)
	cnt = 0
	rval, frame = vc.read()
	while rval:
		cv2.imwrite(f'{save_dir}/{cnt}.jpg', frame)
		cnt += 1
		rval, frame = vc.read()
	print(f"video to {cnt} imgs done")


def gif2img(infile, save_dir=None):
    if not save_dir:
        save_dir = infile.rsplit('.', 1)[0]
    try:
        im = Image.open(infile)
    except IOError:
        print("Cant load", infile)
    ensure_dir(save_dir)
    cnt = 0
    palette = im.getpalette()
    try:
        while True:
            if not im.getpalette():
                im.putpalette(palette)
            new_im = Image.new("RGBA", im.size)
            new_im.paste(im)
            new_im.save(f'{save_dir}/{cnt}.png')
            cnt += 1
            im.seek(im.tell() + 1)
    except EOFError:
        print(f"gif to {cnt} imgs done")
    return cnt


def fontset(ttf, chars=None, img_size=[256,256], font_size=240, background="black", bg_value=(255,255,255), start_pos=(8,8), save_dir=''):
	assert chars != None, 'The chars can not be None.'
	font = ImageFont.truetype(ttf, font_size)
	font_dir = ttf.rstrip('.ttf') if save_dir == '' else save_dir
	ensure_dir(font_dir)
	for c in chars:
		try:
			im = Image.new("RGB", img_size, background)
			im_draw = ImageDraw.Draw(im)
			im_draw.text(start_pos, c, bg_value, font)
			im.save(f"{font_dir}/{c}.png")
		except:
			print(f'Process {c} error.')
			return False
	return True
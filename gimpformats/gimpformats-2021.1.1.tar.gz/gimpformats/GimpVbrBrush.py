#!/usr/bin/env python3
"""Pure python implementation of the gimp vbr brush format.
"""
from __future__ import annotations

from io import BytesIO


class GimpVbrBrush:
	"""Pure python implementation of the gimp vbr brush format.

	See:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/vbr.txt
	"""

	BRUSH_SHAPES = ["circle", "square", "diamond"]

	def __init__(self, fileName: BytesIO | str | None = None):
		"""Pure python implementation of the gimp vbr brush format.

		Args:
			fileName (BytesIO, str, optional): filename. Defaults to None.
		"""
		self.version = 1.0
		self.name = ""
		self.spacing = 0
		self.radius = 50
		self.hardness = 1
		self.aspectRatio = 1
		self.angle = 0
		self.brushShape = None  # one of the strings in self.BRUSH_SHAPES
		self.spikes = None
		if fileName is not None:
			self.load(fileName)

	def load(self, fileName: BytesIO | str):
		"""Load a gimp file.

		:param fileName: can be a file name or a file-like object
		"""
		if isinstance(fileName, str):
			self.fileName = fileName
			file = open(fileName, "rb")
		else:
			self.fileName = fileName.name
			file = fileName
		data = file.read()
		file.close()
		self.decode(data)

	@property
	def image(self):
		"""This parametric brush converted to a useable PIL image."""
		raise NotImplementedError()  # TODO:

	def decode(self, dataIn: bytes):
		"""Decode a byte buffer.

		:param dataIn: data buffer to decode
		"""
		data = [s.strip() for s in dataIn.decode("utf-8").split("\n")]
		if data[0] != "GIMP-VBR":
			raise Exception("File format error.  Magic value mismatch.")
		self.version = float(data[1])
		if self.version == 1.0:
			self.name = data[2]  # max len 255 bytes
			self.spacing = float(data[3])
			self.radius = float(data[4])
			self.hardness = float(data[5])
			self.aspectRatio = float(data[6])
			self.angle = float(data[7])
		elif self.version == 1.5:
			self.name = data[2]  # max len 255 bytes
			self.brushShape = data[3]  # one of the strings in self.BRUSH_SHAPES
			self.spacing = float(data[4])
			self.radius = float(data[5])
			self.spikes = float(data[6])
			self.hardness = float(data[7])
			self.aspectRatio = float(data[8])
			self.angle = float(data[9])
		else:
			raise Exception("Unknown version " + str(self.version))

	def encode(self):
		"""Encode to a raw data stream."""
		data = []
		data.append("GIMP-VBR")
		data.append(str(self.version))
		if self.version == 1.0:
			data.append(str(self.name))
			data.append(str(self.spacing))
			data.append(str(self.radius))
			data.append(str(self.hardness))
			data.append(str(self.aspectRatio))
			data.append(str(self.angle))
		elif self.version == 1.5:
			data.append(str(self.name))
			data.append(str(self.brushShape))
			data.append(str(self.spacing))
			data.append(str(self.radius))
			data.append(str(self.spikes))
			data.append(str(self.hardness))
			data.append(str(self.aspectRatio))
			data.append(str(self.angle))
		return ("\n".join(data) + "\n").encode("utf-8")

	def save(self, tofileName=None, toExtension=None):
		"""Save this gimp image to a file."""
		asImage = False
		if toExtension is None:
			if tofileName is not None:
				toExtension = tofileName.rsplit(".", 1)
				if len(toExtension) > 1:
					toExtension = toExtension[-1]
				else:
					toExtension = None
		if toExtension is not None and toExtension != "vbr":
			asImage = True
		if asImage:
			self.image.save(tofileName)
		else:
			if hasattr(tofileName, "write"):
				file = tofileName
			else:
				file = open(tofileName, "wb")
			file.write(self.encode())
			file.close()

	def __repr__(self):
		"""Get a textual representation of this object."""
		ret = []
		if self.fileName is not None:
			ret.append("fileName: " + self.fileName)
		ret.append("Name: " + str(self.name))
		ret.append("Version: " + str(self.version))
		ret.append("Spacing: " + str(self.spacing))
		ret.append("Radius: " + str(self.radius))
		ret.append("Hardness: " + str(self.hardness))
		ret.append("Aspect ratio: " + str(self.aspectRatio))
		ret.append("Angle: " + str(self.angle))
		ret.append("Brush Shape: " + str(self.brushShape))
		ret.append("Spikes: " + str(self.spikes))
		return "\n".join(ret)

	def __eq__(self, other):
		"""Perform a comparison."""
		if other.name != self.name:
			return False
		if other.version != self.version:
			return False
		if other.spacing != self.spacing:
			return False
		if other.radius != self.radius:
			return False
		if other.hardness != self.hardness:
			return False
		if other.aspectRatio != self.aspectRatio:
			return False
		if other.angle != self.angle:
			return False
		if other.brushShape != self.brushShape:
			return False
		if other.spikes != self.spikes:
			return False
		return True

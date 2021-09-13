import numpy as np
import hashlib
from tqdm import trange
from pathlib import Path
from natsort import natsorted
from overrides import overrides
from functools import partial
from typing import List, Optional, Tuple, Dict
from media_processing_lib.image import tryReadImage, imgResize
from ..dataset import Dataset
from ...utils import unrealPngFromFloat, unrealFloatFromPng, npGetInfo
from .carla_png_reader import CarlaPNGReader

def defaultGetter(d, i, k):
	return np.load(d[k][i])

class CarlaNPYReader(Dataset):
	# 3 layers of "dims": What user wants (dataDims), what is supported by reader and what we actually find on disk.
	def __init__(self, baseDir:Path, dataDims:Optional[List[str]], resolution:Tuple[int,int], hyperParameters:Dict):
		self.baseDir = Path(baseDir).absolute()
		foundDataDims = self.getDataDims()
		supportedDims = ["rgb", "semantic_segmentation", "halftone", "normal", "cameranormal", "wireframe", \
			"depth", "wireframe_regression", "optical_flow(t-1, t)"]
		dataDims = dataDims if not dataDims is None else foundDataDims

		for D in foundDataDims:
			assert D in supportedDims, "%s not in %s" % (D, supportedDims)
		for D in dataDims:
			assert D in foundDataDims

		supportedDimGetter = {k : partial(defaultGetter, k=k) for k in supportedDims}
		supportedDataTransform  = {
			"rgb":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"halftone":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"normal":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"cameranormal":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"semantic_segmentation":partial(CarlaPNGReader.semanticSegmentationTransformer, Obj=self),
			"wireframe":partial(CarlaPNGReader.wireframeTransformer, Obj=self),
			"wireframe_regression":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"depth":partial(CarlaPNGReader.depthTransformer, Obj=self),
		}
		dimGetter = {k : supportedDimGetter[k] for k in foundDataDims}
		dataTransform = {k : supportedDataTransform[k] for k in foundDataDims}

		super().__init__(
			dataBuckets = {"data":foundDataDims},
			dimGetter = dimGetter,
			dimTransform = {"data":dataTransform}
		)

		# self.desiredDataDims = dataDims
		self.hyperParameters = hyperParameters
		self.inFiles = None
		self.buildDataset()
		self.resolution = resolution
		self.isCacheable = False

	# For Npy reader, we expect a structure of:
	# baseDir/
	#   dataDim1/0.npy, ..., N.npy
	#   ...
	#   dataDimM/0.npy, ..., N.npy
	def getDataDims(self):
		dataDims = list(filter(lambda x : x.is_dir(), self.baseDir.iterdir()))
		dataDims = [str(x).split("/")[-1] for x in dataDims]
		print("[CarlaNPYReader::getDataDims] Found data dims: %s" % dataDims)
		if "wireframe" in dataDims:
			dataDims.append("wireframe_regression")
		return dataDims

	def buildDataset(self):
		def getInFiles(baseDir:Path, dataBuckets:List):
			filesNpy = baseDir / "files.npy"
			if filesNpy.exists():
				print("[CarlaNPYReader::builDataset] Reading from %s" % filesNpy)
				inFiles = np.load(filesNpy, allow_pickle=True).item()
				assert len(inFiles.keys()) == len(dataBuckets), "%s vs %s" % (inFiles.keys(), dataBuckets)
			else:
				inFiles = {}
				print("[CarlaNPYReader::builDataset] Building manually from %s" % baseDir)
				for dim in self.datasetFormat.dataBuckets["data"]:
					Dir = self.baseDir / dim
					items = [x for x in Dir.glob("*.npy")]
					items = natsorted([str(x) for x in items])
					inFiles[dim] = items
				if "wireframe_regression" in self.datasetFormat.dataBuckets["data"]:
					inFiles["wireframe_regression"] = inFiles["wireframe"]
				np.save(filesNpy, inFiles)
			return inFiles

		dataBuckets = self.datasetFormat.dataBuckets["data"]
		assert self.inFiles == None
		inFiles = getInFiles(baseDir=self.baseDir, dataBuckets=dataBuckets)
		assert len(inFiles) > 0
		K = list(inFiles.keys())[0]
		Lens = [len(x) for x in inFiles.values()]
		assert np.std(Lens) == 0, "Lens: %s" % dict(zip(dataBuckets, Lens))
		print("[CarlaNPYReader::builDataset] Found %d images for representations %s" % (len(inFiles[K]), dataBuckets))
		self.inFiles = inFiles

	@overrides
	def getDataset(self):
		if self.inFiles is None:
			self.buildDataset()
		return self.inFiles

	@overrides
	def __len__(self) -> int:
		D = self.getDataset()
		return len(D[list(D.keys())[0]])

	@overrides
	def processRawData(**kwargs):
		inputDir = kwargs["inputDir"]
		outputDir = kwargs["outputDir"]
		resolution = kwargs["resolution"]
		hyperParameters = kwargs["hyperParameters"]
		print("[CarlaNpyReader::processRawData] Png dir: %s. Out dir: %s. Resolution: %dx%d" % \
			(inputDir, outputDir, resolution[0], resolution[1]))
		pngReader = CarlaPNGReader(inputDir, dataDims=None, resolution=resolution, \
			deltas=[-1], hyperParameters=hyperParameters)
		buckets = pngReader.datasetFormat.dataBuckets["data"]
		outputDir = Path(outputDir)
		def defaultF(x, height, width):
			return imgResize(x, height=height, width=width, resizeLib="skimage", interpolation="bilinear")
		def semaF(x, height, width):
			# Converting 24-bit to float and to 24-bit back, so we are sure that nearest keeps the unique values only
			#  and does not interpolate inbetween the RGB 3 channels.
			y = unrealFloatFromPng(x)
			y = imgResize(y, height=height, width=width, resizeLib="lycon", interpolation="nearest", onlyUint8=False)
			y = unrealPngFromFloat(y, equalCheck=False)
			return y
		def floatResizeF(x, height, width):
			x = imgResize(x, height=height, width=width, resizeLib="skimage", interpolation="bilinear", onlyUint8=False)
			return x

		# Updated dim transforms to _ONLY_ resize, so we skip this part when we load npy files.
		for D in buckets:
			if "semantic_segmentation" in D:
				f = semaF
			elif "depth" in D or "optical_flow" in D:
				f = floatResizeF
			else:
				f = defaultF
			pngReader.datasetFormat.dimTransform["data"][D]	= partial(f, height=resolution[0], width=resolution[1])

		outputDir.mkdir(exist_ok=True)
		for D in buckets:
			(outputDir / D).mkdir(exist_ok=True)

		for i in trange(len(pngReader)):
			item = pngReader[i]
			for D in buckets:
				inFile = item["data"][D]
				outPath = outputDir / D / ("%d.npy" % i)
				np.save(outPath, inFile)

	@overrides
	def __cache__(self):
		# Cache key is based on 3 parts:
		# Part1: Type + length
		#  <class 'nwdata.custom.batched_algorithms.static_batched_dataset.StaticBatchedDataset'> =>
		#  nwdata.custom.batched_algorithms.static_batched_dataset.StaticBatchedDataset
		Part1 = "%s-%d" % (str(type(self)).split(" ")[-1][1:-2], len(self))
		# Part2: data dims as string: ['rgb', 'semantic_segmentation'] => 'rgb_semantic_segmentation'
		dataBuckets = sorted(self.datasetFormat.dataBuckets["data"])
		Part2 = "_".join(dataBuckets)
		# Part3: getInfo of 1st item
		Item = self[0]
		Infos = {k : npGetInfo(Item["data"][k]) for k in dataBuckets}
		Part3 = str(Infos)

		# Convert the key to md5 for name shrinking
		Str = "%s-%s-%s" % (Part1, Part2, Part3)
		Key = hashlib.md5(Str.encode("utf-8")).hexdigest()
		print("[CarlaPNGReader::__cache__] Cache key: md5(%s)=%s" % (Str, Key))
		return Key

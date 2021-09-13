import numpy as np
import hashlib
from pathlib import Path
from natsort import natsorted
from overrides import overrides
from copy import copy
from functools import partial
from typing import List, Optional, Tuple, Dict
from media_processing_lib.image import tryReadImage, imgResize
from ..dataset import Dataset
from ...utils import unrealFloatFromPng, npGetInfo

class CarlaPNGReader(Dataset):
	def __init__(self, baseDir:Path, dataDims:Optional[List[str]], resolution:Tuple[int,int], \
		deltas:List[int]=[], hyperParameters:Dict={}):
		self.baseDir = Path(baseDir).absolute()
		allDataDims = self.getDataDims()

		dimGetter = {
			"rgb":partial(CarlaPNGReader.defaultGetter, dim="rgb"),
			"semantic_segmentation":partial(CarlaPNGReader.defaultGetter, dim="semantic_segmentation"),
			"halftone":partial(CarlaPNGReader.defaultGetter, dim="halftone"),
			"normal":partial(CarlaPNGReader.defaultGetter, dim="normal"),
			"cameranormal":partial(CarlaPNGReader.defaultGetter, dim="cameranormal"),
			"wireframe":partial(CarlaPNGReader.defaultGetter, dim="wireframe"),
			"wireframe_regression":partial(CarlaPNGReader.defaultGetter, dim="wireframe"),
			"depth":partial(CarlaPNGReader.depthGetter, dim="depth"),
			"optical_flow(t-1, t)":CarlaPNGReader.opticalFlowGetter
		}
		dataTransform  = {
			"rgb":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"halftone":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"normal":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"cameranormal":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"semantic_segmentation":partial(CarlaPNGReader.semanticSegmentationTransformer, Obj=self),
			"wireframe":partial(CarlaPNGReader.wireframeTransformer, Obj=self),
			"wireframe_regression":partial(CarlaPNGReader.defaultTransformer, Obj=self),
			"depth":partial(CarlaPNGReader.depthTransformer, Obj=self),
			"optical_flow(t-1, t)":partial(CarlaPNGReader.opticalFlowTransformer, Obj=self)
		}
		allDataDims = list(set(allDataDims).intersection(dimGetter))
		self.noDeltaAllDims = copy(allDataDims)
		allDataDims, dimGetter, dataTransform = self.addDeltas(allDataDims, dimGetter, dataTransform, deltas)

		if dataDims is None:
			dataDims = allDataDims
		for D in dataDims:
			assert D in allDataDims, "%s vs %s" % (dataDims, allDataDims)
		dimGetter = {k : dimGetter[k] for k in allDataDims}
		dataTransform = {k : dataTransform[k] for k in allDataDims}

		super().__init__(
			dataBuckets = {"data":allDataDims},
			dimGetter = dimGetter,
			dimTransform = {"data":dataTransform}
		)

		self.desiredDataDims = dataDims
		self.hyperParameters = hyperParameters
		self.inFiles = None
		self.resolution = resolution
		self.deltas = deltas
		self.isCacheable = True

	def addDeltas(self, allDataDims, dimGetter, dataTransform, deltas):
		# deltas=[-1, 1] => rgb(t-1) and rgb(t+1)
		for k in self.noDeltaAllDims:
			if k == "optical_flow(t-1, t)":
				continue
			for delta in deltas:
				assert delta < 0 or delta > 0
				K = "%s(t%+d)" % (k, delta)
				allDataDims.append(K)
				dimGetter[K] = partial(dimGetter[k], delta=delta)
				dataTransform[K] = dataTransform[k]
		return allDataDims, dimGetter, dataTransform

	def addInFilesDeltas(self, inFiles):
		for k in self.noDeltaAllDims:
			if k == "optical_flow(t-1, t)":
				continue
			for delta in self.deltas:
				assert delta < 0 or delta > 0
				K = "%s(t%+d)" % (k, delta)
				inFiles[K] = inFiles[k]
		return inFiles

	@staticmethod
	def defaultTransformer(x, Obj):
		height, width = Obj.resolution
		x = imgResize(x, height=height, width=width, resizeLib="skimage", interpolation="bilinear")
		x = np.float32(x) / 255
		return x

	@staticmethod
	def defaultGetter(x, ix, dim:str, delta=0):
		x = x[dim]
		ix = np.clip(ix + delta, 0, len(x) - 1)
		path = x[ix]
		img = tryReadImage(path)
		return img

	@staticmethod
	def depthTransformer(x, Obj):
		height, width = Obj.resolution
		maxDepthMeters = Obj.hyperParameters["maxDepthMeters"]
		x = imgResize(x, height=height, width=width, resizeLib="skimage", onlyUint8=False)
		# Depth is stored as [0:1] representing [0:1000m] range
		x = np.clip(x * 1000, 0, maxDepthMeters)
		x = x / maxDepthMeters
		x = np.expand_dims(x, axis=-1)
		return x

	@staticmethod
	def depthGetter(x, ix, dim, delta=0):
		img = CarlaPNGReader.defaultGetter(x, ix, dim, delta)
		depth = unrealFloatFromPng(img)
		return depth

	@staticmethod
	def wireframeTransformer(x, Obj):
		x = x[..., 0 : 1]
		x = np.float32(x > 0)
		return x

	@staticmethod
	def semanticSegmentationTransformer(x, Obj):
		semanticClasses = Obj.hyperParameters["semanticClasses"]
		height, width = Obj.resolution
		allClasses = {
			"Unlabeled":(0, 0, 0),
			"Building":(70, 70, 70),
			"Fence":(153, 153, 190),
			"Other":(160, 170, 250),
			"Pedestrian":(60, 20, 220),
			"Pole":(153, 153, 153),
			"Road line":(50, 234, 157),
			"Road":(128, 64, 128),
			"Sidewalk":(232, 35, 244),
			"Vegetation":(35, 142, 107),
			"Car":(142, 0, 0),
			"Wall":(156, 102, 102),
			"Traffic sign":(0, 220, 220)
		}
		# Optimization if we're going to support a lot of classes and we just care about a small subset
		if isinstance(semanticClasses[0], str):
			allClasses = dict([(k, allClasses[k]) for k in semanticClasses])
		NC = len(semanticClasses)

		x = imgResize(x, height=height, width=width, resizeLib="lycon", interpolation="nearest")
		x = x.reshape((height * width, 3))
		result = np.zeros((height * width, NC), dtype=np.uint8)
		for i, value in enumerate(allClasses.values()):
			condition = (x == value).sum(-1) == 3
			Where = np.where(condition)[0]
			result[Where, i] = 1
		result = result.reshape((height, width, NC))
		return result

	@staticmethod
	def opticalFlowGetter(x, ix):
		path_x = x["optical_flow(t-1, t)"][ix][0]
		path_y = x["optical_flow(t-1, t)"][ix][1]

		img_x = tryReadImage(path_x)
		img_y = tryReadImage(path_y)

		flow_x = unrealFloatFromPng(img_x)
		flow_y = unrealFloatFromPng(img_y)

		flow = np.stack([flow_x, flow_y], axis=-1)
		return flow

	@staticmethod
	def opticalFlowTransformer(x, Obj):
		height, width = Obj.resolution
		y = imgResize(x, height=height, width=width, resizeLib="skimage", interpolation="bilinear", onlyUint8=False)
		return y

	def getDataDims(self):
		J = [str(x) for x in self.baseDir.glob("*.png")]
		J = [x.split("/")[-1].split("_")[1] for x in J]
		dataDims = np.unique(J).tolist()
		if "semanticSegmentation" in J:
			dataDims.pop(dataDims.index("semanticSegmentation"))
			dataDims.append("semantic_segmentation")
		if "wireframe" in dataDims:
			dataDims.append("wireframe_regression")
		if "flowr2" in J:
			assert "flowr3" in J
			dataDims.pop(dataDims.index("flowr2"))
			dataDims.pop(dataDims.index("flowr3"))
			dataDims.append("optical_flow(t-1, t)")

		print("[CarlaPNGReader::getDataDims] No data dims were provided. Using all available: %s" % dataDims)
		return dataDims

	def buildInFiles(self, baseDir:Path, dataBuckets:List):
		inFiles = {}
		print("[CarlaPNGReader::builDataset] Building manually from %s" % baseDir)
		for dim in dataBuckets:
			if dim == "semantic_segmentation":
				items = [x for x in baseDir.glob("*_semanticSegmentation_*")]
				items = natsorted([str(x) for x in items])
			elif dim == "optical_flow(t-1, t)":
				# Key = "flowr2"
				items_x = [x for x in baseDir.glob("*_flowr2_*")]
				items_x = natsorted([str(x) for x in items_x])
				items_y = [x for x in baseDir.glob("*_flowr3_*")]
				items_y = natsorted([str(x) for x in items_y])
				items = [(x, y) for x, y in zip(items_x, items_y)]
			elif dim == "wireframe_regression":
				assert "wireframe" in dataBuckets
				items = [x for x in baseDir.glob("*_wireframe_*")]
				items = natsorted([str(x) for x in items])
			else:
				Key = dim
				items = [x for x in baseDir.glob("*_%s_*" % Key)]
				items = natsorted([str(x) for x in items])
			inFiles[dim] = items
		return inFiles

	def buildDataset(self):
		dataBuckets = self.datasetFormat.dataBuckets["data"]
		assert self.inFiles == None
		filesNpy = self.baseDir / "files.npy"
		if filesNpy.exists():
			print("[CarlaPNGReader::builDataset] Reading from %s" % filesNpy)
			inFiles = np.load(filesNpy, allow_pickle=True).item()
		else:
			inFiles = self.buildInFiles(baseDir=self.baseDir, dataBuckets=dataBuckets)
			np.save(self.baseDir / "files.npy", inFiles)

		inFiles = self.addInFilesDeltas(inFiles)
		assert len(inFiles) > 0
		breakpoint()
		Lens = [len(x) for x in inFiles.values()]
		K = list(inFiles.keys())
		assert np.std(Lens) == 0, "Lens: %s" % dict(zip(dataBuckets, Lens))
		print("[CarlaPNGReader::builDataset] Found %d images for representations %s" % (len(inFiles[K[0]]), K))
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
		pass

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

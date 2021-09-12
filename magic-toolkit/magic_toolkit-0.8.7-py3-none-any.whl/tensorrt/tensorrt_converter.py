from magic.base import BaseConverter
from magic.config_templates import get_config_template
from magic.config import configParser
import os
import sys
import importlib

class Onnx2trtConverter(BaseConverter):
    def __init__(self, sub_parsers):
        p = sub_parsers.add_parser("onnx2trt", help="convert onnx to tensorrt")
        p.add_argument("config", default="", help="give config.yaml or get-config")

    def load_preprocess_fn(self, py_file):
        dir = os.path.dirname(py_file)
        base = os.path.basename(py_file)
        sys.path.append(dir)
        sys.dont_write_bytecode = True
        module_name = base.split(".")[0]
        m = importlib.import_module(module_name)
        preprocess_fn = getattr(m, "preprocess_fn", None)
        if preprocess_fn is None:
            raise RuntimeError("couldn't find: preprocess_fn in {}".format(py_file))
        else:
            return preprocess_fn

    def execute(self, args):
        if args.config == "get-config":
            get_config_template("onnx2trt_config.yaml")
            return
        cfg = configParser(args.config)
        calibrator = None
        if cfg.int8 and cfg.calibrator.data_type == "image":
            preprocess_fn = self.load_preprocess_fn(cfg.calibrator.preprocess_fn)
            from .img_calibrator import ImgEntropyCalibrator
            calibrator = ImgEntropyCalibrator(cfg.calibrator.data_dir,
                                              cfg.calibrator.batch,
                                              cfg.calibrator.input_size,
                                              cfg.calibrator.num_random_samples,
                                              preprocess_fn=preprocess_fn,
                                              cache_file=cfg.calibrator.calibration_file)
        from .onnx2trt import onnx_convert
        onnx_convert(cfg.onnx_path, cfg.trt_path, cfg.batch, cfg.fp16, cfg.int8, calibrator, cfg.verbose)

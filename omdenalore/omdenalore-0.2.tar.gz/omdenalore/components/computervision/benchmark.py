# Adapted from: https://github.com/rwightman/pytorch-image-models/blob/bd5694667625d510e3aa89e95397de97d0e7efe9/benchmark.py

import time
import os
from contextlib import suppress
from functools import partial
import torch
import torch.nn as nn
from .utils import Params

amp = False
try:
    if getattr(torch.cuda.amp, "autocast") is not None:
        amp = True
except AttributeError:
    pass
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def timestamp(sync: bool = False):
    """
    returns time.perf_counter
    """
    return time.perf_counter()


def cuda_timestamp(sync: bool = False, device=None):
    """
    synchronizes cuda device if sync is true

    :param sync: boolean value deciding whether to sync
    :type sync: boolean
    :param device: cuda device
    :type device: torch.cuda.device
    """
    if sync:
        torch.cuda.synchronize(device=device)
    return time.perf_counter()


def count_params(model: nn.Module):
    """
    returns the number of parameters of the model

    :param model: neural network model
    :type model: nn.Module
    """
    return sum([m.numel() for m in model.parameters()])


def resolve_precision(precision: str):
    """
    Resolves the precision of the data type

    :param precision: precision data type passed in
    :type precision: str
    """
    assert precision in ("float16", "bfloat16", "float32")
    use_amp = False
    model_dtype = torch.float32
    data_dtype = torch.float32
    if amp:
        use_amp = True
    elif precision == "float16":
        model_dtype = torch.float16
        data_dtype = torch.float16
    elif precision == "bfloat16":
        model_dtype = torch.bfloat16
        data_dtype = torch.bfloat16
    return use_amp, model_dtype, data_dtype


class BenchmarkRunner:
    """
    Base class which can be extended to inference or traning benchmark.

    :param model_dir: path to folder containing `params.json` file
    :type model_dir: str
    :param num_warm_iter: number of iterations as warmup
    :type num_warm_iter: int
    :param num_bench_iter: number of iterations to benchmark
    :type num_bench_iter: int
    :param precision: precision to use for benchmarking ["float16", "float32", "bfloat16"]
    :type precision: str

    """

    def __init__(
        self,
        model_dir: str,
        num_warm_iter: int = 10,
        num_bench_iter: int = 50,
        precision: str = "float16",
    ):
        """
        :param model_dir: directory from where the model is loaded
        :type model_dir: str
        :param num_warm_iter: warming steps for training
        :type num_warm_iter: int
        :param num_bench_iter: benchmark iterations
        :type num_bench_iter: int
        :param precision: precision value for threshold
        :type precision: str
        """

        json_path = os.path.join(model_dir, "params.json")
        assert os.path.isfile(
            json_path
        ), "No json configuration file found at {}".format(json_path)
        params = Params(json_path)
        self.use_amp, self.model_dtype, self.data_dtype = resolve_precision(precision)
        self.amp_autocast = torch.cuda.amp.autocast if self.use_amp else suppress
        print(f"Loading model from path {params.save_model_path}")
        self.model = torch.load(params.save_model_path).to(
            device=device, dtype=self.model_dtype
        )
        self.param_count = count_params(self.model)
        self.num_classes = params.num_classes
        print("Model created, param count: %d" % (self.param_count))
        self.data_h, self.data_w, self.data_d = (
            params.height,
            params.width,
            params.input_channels,
        )
        self.input_size = (self.data_d, self.data_h, self.data_w)
        self.batch_size = params.batch_size
        self.num_warm_iter = num_warm_iter
        self.num_bench_iter = num_bench_iter
        self.log_freq = num_bench_iter // 5
        if torch.cuda.is_available():
            self.time_fn = partial(cuda_timestamp, device=device)
        else:
            self.time_fn = timestamp

    def _init_input(self):
        """
        make example inputs
        """
        # (NCHW)
        self.example_inputs = torch.randn(
            (self.batch_size,) + self.input_size, device=device, dtype=self.data_dtype
        )


class InferenceBenchmarkRunner(BenchmarkRunner):
    """
    Inference class extended from :class:`BenchmarkRunner`

    :param model_dir: path to folder containing `params.json` file
    :type model_dir: str
    :param precision: precision to use for benchmarking ["float16", "float32", "bfloat16"]
    :type precision: str

    """

    def __init__(self, model_dir: str, precision: str = "float32"):
        """
        :param model_dir: directory where to load the model from
        :type model_dir: str
        :param precision: data type precision
        :type precision: str
        """
        super().__init__(model_dir=model_dir, precision=precision)
        self.model.eval()

    def run(self):
        """
        Run the neural network model
        """

        def _step():
            t_step_start = self.time_fn()
            with self.amp_autocast():
                output = self.model(self.example_inputs)
            t_step_end = self.time_fn(True)
            return t_step_end - t_step_start

        print(
            f"Running inference benchmark on the model for {self.num_bench_iter} steps w/ "
            f"input size {self.input_size} and batch size {self.batch_size}."
        )

        with torch.no_grad():
            self._init_input()

            for _ in range(self.num_warm_iter):
                _step()

            total_step = 0.0
            num_samples = 0
            t_run_start = self.time_fn()
            for i in range(self.num_bench_iter):
                delta_fwd = _step()
                total_step += delta_fwd
                num_samples += self.batch_size
                num_steps = i + 1
                if num_steps % self.log_freq == 0:
                    print(
                        f"Infer [{num_steps}/{self.num_bench_iter}]."
                        f" {num_samples / total_step:0.2f} samples/sec."
                        f" {1000 * total_step / num_steps:0.3f} ms/step."
                    )
            t_run_end = self.time_fn(True)
            t_run_elapsed = t_run_end - t_run_start

        results = dict(
            samples_per_sec=round(num_samples / t_run_elapsed, 2),
            step_time=round(1000 * total_step / self.num_bench_iter, 3),
            batch_size=self.batch_size,
            img_size=self.input_size[-1],
            param_count=round(self.param_count / 1e6, 2),
        )

        print(
            f"Inference benchmark of the model done. "
            f"{results['samples_per_sec']:.2f} samples/sec, {results['step_time']:.2f} ms/step"
        )
        return results

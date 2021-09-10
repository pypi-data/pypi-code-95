#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

MAJOR = 0
MINOR = 0
PATCH = 1
PRE_RELEASE = 'dev5'
# Use the following formatting: (major, minor, patch, prerelease)
VERSION = (MAJOR, MINOR, PATCH, PRE_RELEASE)

__shortversion__ = '.'.join(map(str, VERSION[:3]))
__version__ = '.'.join(map(str, VERSION[:3])) + "%s" % ''.join(VERSION[3:])

__contact_names__ = 'Jonathan Dekhtiar'
__contact_emails__ = 'jdekhtiar@nvidia.com'
__homepage__ = 'https://github.com/NVIDIA'
__repository_url__ = 'https://github.com/NVIDIA'
__download_url__ = 'https://github.com/NVIDIA'
__description__ = 'A fake package to warn the user they are not installing ' \
                  'the correct package.'
__license__ = 'Apache2'
__keywords__ = 'nvidia, deep learning, machine learning, supervised learning,'
__keywords__ += 'unsupervised learning, reinforcement learning, logging'

__faked_packages__ = [
    # Format
    # (package_name, readme_filename, error_filename),

    # Test Package
    ("nvidia-pyindex-test-pkg", None, None),  # Do not remove - @DEKHTIARJonathan

    # DL Frameworks
    ("nvidia-tensorflow", "tensorflow.rst", "tensorflow.txt"),
    ("nvidia-pytorch", None, None),
    ("nvidia-torch", None, None),
    ("nvidia-torchvision", None, None),
    ("nvidia-mxnet", None, None),

    # JoC Team Packages
    ("nvidia-dllogger", "dllogger.rst", "dllogger.txt"),  # ask @ashumak before doing any change

    # JARVIS
    ("nvidia-eff", None, None),  # ask @Tomasz Kornuta before doing any change
    ("nvidia-tlt", None, None),  # ask @Varun Praveen before doing any change
    ("nvidia-jarvis", None, None),  # ask @Jonathan Cohen before doing any change

    # Clara
    ("nvidia-clara-pipeline-driver", None, None),  # ask Alvin Ihsani before doing any change

    # TensorRT owned packages - Ask @Eric Work before doing any change
    ("nvidia-tensorrt", None, None),
    ("graphsurgeon", None, None),
    ("onnx-graphsurgeon", None, None),
    ("polygraphy", None, None),
    ("pytorch-quantization", None, None),
    ("uff", None, None),

    # TF additional libraries
    ("nvidia-tensorflow-estimator", None, None),
    ("nvidia-horovod", None, None),

    # Triton Library - Ask @David Goodwin or @David Zier before doing any change
    ("tritonclient", "tritonclient.rst", "tritonclient.txt"),
    ("triton-model-analyzer", "tritonclient.rst", "tritonclient.txt"),    

    # DALI public wheels - Ask @Janusz Lisiecki before doing any change
    ("nvidia-dali", "dali.rst", "dali.txt"),

    ("nvidia-dali-tf-plugin", "dali.rst", "dali.txt"),

    # DALI TF Plugin wheel used by `nvidia-tensorflow`
    ("nvidia-dali-nvtf-plugin", None, None),

    # DLProf - ask @David Zier before doing any change
    ("nvidia-dlprof", None, None),
    ("nvidia-tensorboard-plugin-dlprof", None, None),
    ("nvidia-tensorboard", None, None),
    ("nvidia-pyprof", None, None),

    # Packages owned by @Robert Clark
    ("nvidia-imageinary", None, None),
    ("nvidia-bobber", None, None),

    # CUDA-X Libraries
    ("nvidia-cublas", None, None),
    ("nvidia-cuda-cupti", None, None),
    ("nvidia-cuda-nvcc", None, None),
    ("nvidia-cuda-nvrtc", None, None),
    ("nvidia-cuda-runtime", None, None),
    ("nvidia-cuda-sanitizer-api", None, None),
    ("nvidia-cudnn", None, None),
    ("nvidia-cufft", None, None),
    ("nvidia-curand", None, None),
    ("nvidia-cusolver", None, None),
    ("nvidia-cusparse", None, None),
    ("nvidia-nccl", None, None),
    ("nvidia-npp", None, None),
    ("nvidia-nsys", None, None),
    ("nvidia-nsys-cli", None, None),
    ("nvidia-nvjpeg", None, None),
    ("nvidia-nvml-dev", None, None),
    ("nvidia-nvtx", None, None),
]

CUDA_9_VERS = [
    "9.0",
    "9.1",
    "9.2"
]

CUDA_10_VERS = [
    "10.0",
    "10.1",
    "10.2"
]

CUDA_11_VERS = [
    "11.0",
    "11.1",
    "11.2",
    "11.3"
]

for __cuda__ in CUDA_9_VERS + CUDA_10_VERS + CUDA_11_VERS:
    __faked_packages__ += [
        (
            "nvidia-dali-cuda{}".format(__cuda__.replace(".", "")),
            "dali.rst",
            "dali.txt"
        ),
        (
            "nvidia-dali-tf-plugin-cuda{}".format(__cuda__.replace(".", "")),
            "dali.rst",
            "dali.txt"
        )
    ]

CUDA_X_PACKAGES = [
    "nvidia-cublas-cu",
    "nvidia-cuda-nvcc-cu",
    "nvidia-cuda-nvrtc-cu",
    "nvidia-cuda-runtime-cu",
    "nvidia-cuda-sanitizer-api-cu",
    "nvidia-cufft-cu",
    "nvidia-curand-cu",
    "nvidia-cusolver-cu",
    "nvidia-cusparse-cu",
    "nvidia-npp-cu",
    "nvidia-nvjpeg-cu",
    "nvidia-nvml-dev-cu",
    "nvidia-nvtx-cu",
    "nvidia-cuda-cupti-cu"
]

for __cuda_pkg__ in CUDA_X_PACKAGES:
    for __cuda__ in CUDA_11_VERS:
        if __cuda__[-2:] == ".0":
            __faked_packages__ += [
                (__cuda_pkg__ + __cuda__.split(".")[0], None, None)
            ]
        __faked_packages__ += [
            (__cuda_pkg__ + __cuda__.replace(".", ""), None, None)
        ]

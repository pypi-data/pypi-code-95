#
# Copyright 2020-2021 Intel Corporation.
#
# LEGAL NOTICE: Your use of this software and any required dependent software
# (the "Software Package") is subject to the terms and conditions of
# the Intel(R) OpenVINO(TM) Distribution License for the Software Package,
# which may also include notices, disclaimers, or license terms for
# third party or open source software included in or with the Software Package,
# and your use indicates your acceptance of all such terms. Please refer
# to the "third-party-programs.txt" or other similarly-named text file
# included with the Software Package for additional details.

from pathlib import Path
import sys

sys.path.insert(0, Path(__file__).resolve().parent.parent.parent.as_posix()) # pylint: disable=C0413
from compression.utils.config_reader import read_config_from_file, write_config_to_file

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

data = read_config_from_file(src)
write_config_to_file(data, dst)

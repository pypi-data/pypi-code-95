#    Copyright 2021 Qruise project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from grpc_tools import protoc
import os

from tempfile import mkstemp
from shutil import move, copymode
import re

def replace(file_path, p, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with os.fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(re.sub(p, subst, line))
    #Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    #Remove original file
    os.remove(file_path)
    #Move new file
    move(abs_path, file_path)

_PROTO_PREFIX = "qcalibrate"

if __name__ == '__main__':
    dir_name = os.path.dirname(os.path.abspath(__file__))

    protoc.main((
        '',
        f'-I{dir_name}',
        f'--python_out={dir_name}',
        f'--grpc_python_out={dir_name}',
        f'{os.path.join(dir_name, f"{_PROTO_PREFIX}.proto")}',
    ))

    files = list(map(lambda f: os.path.join(dir_name,f), filter(lambda s: s.endswith( 'pb2_grpc.py'), os.listdir(dir_name))))

    pattern = re.compile(f'^import {_PROTO_PREFIX}')

    for file in files:
        replace(file, pattern, f'from . import {_PROTO_PREFIX}')


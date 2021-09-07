#  Copyright 2020, 2021 Evandro Chagas Ribeiro da Rosa <evandro.crr@posgrad.ufsc.br>
#  Copyright 2020, 2021 Rafael de Santiago <r.santiago@ufsc.br>
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .kbw import kbw, set_plugin_path, set_seed 
from flask import request, jsonify, Flask
from base64 import b64encode
from random import randint
from os import environ
from os.path import dirname

server = Flask(__name__)

@server.route('/', methods=['GET'])
def home():
    return '''<h1>Ket Bitwise Simulator</h1>
<p><a href=http://quantum-ket.gitlab.io>quantum-ket.gitlab.io</a></p>'''

@server.route('/api/v1/run', methods=['GET'])
def run_kqasm():
    
    if 'kqasm' not in request.form:
        return 'Error!!! No KQASM provided.'

    kqasm = request.form['kqasm']

    plugin_path = environ['KBW_LIBPATH']
    set_plugin_path(plugin_path)

    environ['KET_PYCALL'] = dirname(__file__)+'/ket_pycall_interpreter'

    seed = int(request.args['seed']) if 'seed' in request.args else randint(0, 2**31)
    set_seed(seed)
    
    quantum_execution = kbw(kqasm)
    quantum_execution.run()

    result = {}

    result['int'] = {}
    for i in range(quantum_execution.results_len()):
        result['int'][i] = quantum_execution.get_result(i)

    result['dump'] = {}
    
    if 'dump2fs' in request.args and request.args['dump2fs'] == '1':
        result['dump2fs'] = 1
        for i in range(quantum_execution.dumps_len()):
            result['dump'][i] = quantum_execution.dump_to_fs(i)
    else:
        result['dump2fs'] = 0
        for i in range(quantum_execution.dumps_len()):
            result['dump'][i] = b64encode(quantum_execution.get_dump(i)).decode()
    
    result['seed'] = seed

    return jsonify(result)

def get():
    plugin_path = dirname(__file__)
    environ['KBW_LIBPATH'] = plugin_path
    return server
   

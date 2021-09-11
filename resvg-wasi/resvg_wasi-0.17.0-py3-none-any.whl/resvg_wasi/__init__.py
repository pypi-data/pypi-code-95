import os
import sys
import tempfile
import wasmtime
import pathlib
import hashlib
import appdirs
import lzma
from importlib import resources as importlib_resources
try:
    importlib_resources.files # py3.9+ stdlib
except AttributeError:
    import importlib_resources # py3.8- shim


def _run_wasm_app(wasm_filename, argv, cachedir="resvg-wasi"):

    module_binary = importlib_resources.read_binary(__package__, wasm_filename)

    module_path_digest = hashlib.sha256(__file__.encode()).hexdigest()
    module_digest = hashlib.sha256(module_binary).hexdigest()
    cache_path = pathlib.Path(os.getenv("RESVG_WASI_CACHE_DIR", appdirs.user_cache_dir(cachedir)))
    cache_path.mkdir(parents=True, exist_ok=True)
    cache_filename = (cache_path / f'{wasm_filename}-{module_path_digest[:8]}-{module_digest[:16]}')
    
    wasi_cfg = wasmtime.WasiConfig()
    wasi_cfg.argv = argv
    wasi_cfg.preopen_dir('/tmp', '/tmp')
    wasi_cfg.preopen_dir('/', '/')
    wasi_cfg.preopen_dir('.', '.')
    wasi_cfg.preopen_dir('..', '..')
    wasi_cfg.inherit_stdin()
    wasi_cfg.inherit_stdout()
    wasi_cfg.inherit_stderr()
    engine = wasmtime.Engine()

    import time
    try:
        with cache_filename.open("rb") as cache_file:
            module = wasmtime.Module.deserialize(engine, lzma.decompress(cache_file.read()))
    except:
        print("Preparing to run {}. This might take a while...".format(argv[0]), file=sys.stderr)
        module = wasmtime.Module(engine, module_binary)
        with cache_filename.open("wb") as cache_file:
            cache_file.write(lzma.compress(module.serialize(), preset=0))

    linker = wasmtime.Linker(engine)
    linker.define_wasi()
    store = wasmtime.Store(engine)
    store.set_wasi(wasi_cfg)
    app = linker.instantiate(store, module)
    linker.define_instance(store, "app", app)

    try:
        app.exports(store)["_start"](store)
        return 0
    except wasmtime.ExitTrap as trap:
        return trap.code


def run_usvg():
    sys.exit(_run_wasm_app("usvg.wasm", ["usvg", *sys.argv[1:]]))

def run_resvg():
    sys.exit(_run_wasm_app("resvg.wasm", ["resvg", *sys.argv[1:]]))


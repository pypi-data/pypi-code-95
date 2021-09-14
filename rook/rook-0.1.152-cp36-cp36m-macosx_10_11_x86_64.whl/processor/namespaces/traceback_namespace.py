from .namespace import Namespace
from .python_object_namespace import PythonObjectNamespace
from rook.protobuf import variant_pb2


class TracebackNamespace(Namespace):
    def __init__(self, frame, depth):
        super(TracebackNamespace, self).__init__()
        self._frame = frame
        self._depth = depth

    def __getitem__(self, key):
        return self.read_key(key)

    def call_method(self, name, args):
        if name == "size":
            return PythonObjectNamespace(self._depth)
        else:
            return super(TracebackNamespace, self).call_method(name, args)

    def read_key(self, key):
        pos = int(key)

        current_frame = self._frame

        for i in range(pos):
            current_frame = current_frame.f_back()

        return current_frame

    def dump(self, variant, getStringIndexInCache=None):
        variant.variant_type = variant_pb2.Variant.Type.VARIANT_TRACEBACK

        current_frame = self._frame

        for i in range(self._depth):
            frame = variant_pb2.Variant.CodeObject()

            frame.lineno = current_frame.line().obj if current_frame.line().obj is not None else 0
            if getStringIndexInCache is None:
                frame.filename = current_frame.filename().obj if current_frame.filename().obj is not None else "unavailable"
                frame.name = current_frame.function().obj if current_frame.function().obj is not None else "unavailable"
                frame.module = current_frame.module().obj if current_frame.module().obj is not None else "unavailable"
            else:
                frame.filename_index_in_cache = getStringIndexInCache(current_frame.filename().obj if current_frame.filename().obj is not None else "unavailable")
                frame.name_index_in_cache = getStringIndexInCache(current_frame.function().obj if current_frame.function().obj is not None else "unavailable")
                frame.module_index_in_cache = getStringIndexInCache(current_frame.module().obj if current_frame.module().obj is not None else "unavailable")

            variant.traceback.locations.append(frame)

            current_frame = current_frame.f_back()

            if not current_frame:
                break

"""Copyright Alpine Intuition Sàrl team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64

import cv2
import numpy as np


def serialize_img(array: np.ndarray) -> bytes:
    """Serialize a numpy array into bytes."""
    if array.max() > 255:
        raise ValueError("Can only serialize 16bits images")
    if "int" not in str(array.dtype):
        raise ValueError(f"Array dtype must be 'uint8', got {array.dtype}")
    success, encoded_array = cv2.imencode(".png", array)
    if not success:
        raise ValueError("Fail to encode array")
    return base64.b64encode(encoded_array)


def deserialize_img(serialized_array: bytes) -> np.ndarray:
    """Serialize a bytes variable into numpy array."""
    decoded_array = base64.b64decode(serialized_array)
    decoded_array = np.frombuffer(decoded_array, np.uint8)
    decoded_array = cv2.imdecode(decoded_array, cv2.IMREAD_UNCHANGED)
    if decoded_array is None:
        raise ValueError("Fail to decode serialized array")
    return decoded_array

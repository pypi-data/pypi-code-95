import sys
import os
print(sys.path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
print(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
print(sys.path)

import geometry
print(geometry.__all__)

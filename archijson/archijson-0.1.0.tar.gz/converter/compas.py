from geometry import Vertices, Faces, Mesh
from itertools import chain

def to_mesh(vs, fs):
    assert (type(vs) == list) & (type(vs[0]) == list)
    assert (type(fs) == list) & (type(fs[0]) == list)

    v_size = len(vs[0])
    v_coords = list(chain(*vs))

    v = Vertices(v_coords, v_size)
    
    f_index = []
    f_count = []
    f_size = []
    
    mp = {}
    for id, face in enumerate(fs):
        try:
            mp[len(face)].append(id)
        except Exception:
            mp[len(face)] = [id]
        
    for size in mp:
        idx = mp[size]

        f_size.append(size)
        f_count.append(len(idx))

        for id in idx:
            f_index.extend(fs[id])
    
    f = Faces(f_count, f_size, f_index)
    return Mesh(v, f)

# def test_make_raster():
#     """
#     test stational function _make_raster of AERFolderDataset
#     raster count of spike events per timestep
#     """
#     import numpy as np
#     from aermanager import AERFolderDataset
#     from .utils import init_data
#
#     events_struct, _, _ = init_data()
#     train = np.array(
#         [(1, 0, 0, False), (0, 1, 2, False), (1, 1, 2, False), (1, 1, 2, False), (0, 1, 3, False)],
#         dtype=events_struct,
#     )
#     raster = np.array([[[[0, 0], [1, 0]]], [[[0, 0], [0, 0]]], [[[0, 1], [0, 2]]], [[[0, 1], [0, 0]]]])
#
#     bins = np.linspace(0, 1, 3)
#     output = AERFolderDataset._make_raster(train, 1, (bins, bins))
#     print(output)
#     assert np.array_equal(raster, output)

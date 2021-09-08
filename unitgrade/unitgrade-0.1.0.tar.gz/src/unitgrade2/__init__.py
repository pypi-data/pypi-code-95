import unitgrade2.version as __version__
from unitgrade2.unitgrade2 import myround, mfloor, msum, Capturing, ActiveProgress, Report, UTestCase
from unitgrade2.unitgrade_helpers2 import evaluate_report_student

# import os
# import lzma
# import pickle

# DONT't import stuff here since install script requires __version__

# def cache_write(object, file_name, verbose=True):
#     # raise Exception("bad")
#     # import compress_pickle
#     dn = os.path.dirname(file_name)
#     if not os.path.exists(dn):
#         os.mkdir(dn)
#     if verbose: print("Writing cache...", file_name)
#     with lzma.open(file_name, 'wb', ) as f:
#         pickle.dump(object, f)
#     if verbose: print("Done!")
#
#
# def cache_exists(file_name):
#     # file_name = cn_(file_name) if cache_prefix else file_name
#     return os.path.exists(file_name)
#
#
# def cache_read(file_name):
#     # import compress_pickle # Import here because if you import in top the __version__ tag will fail.
#     # file_name = cn_(file_name) if cache_prefix else file_name
#     if os.path.exists(file_name):
#         try:
#             with lzma.open(file_name, 'rb') as f:
#                 return pickle.load(f)
#         except Exception as e:
#             print("Tried to load a bad pickle file at", file_name)
#             print("If the file appears to be automatically generated, you can try to delete it, otherwise download a new version")
#             print(e)
#             # return pickle.load(f)
#     else:
#         return None


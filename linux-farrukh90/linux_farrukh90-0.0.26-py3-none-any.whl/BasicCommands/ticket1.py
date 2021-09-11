

import sys
sys.path.append('../')

from Classes.shared_scripts.modules import *
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def taskchecker():
    filechecker("/tmp/services")
    filechecker("/tmp/passwd")
    filechecker("/tmp/.secret")
    folderchecker("/tmp/Photos")
    folderchecker("/tmp/Photos/Hawaii")
    folderchecker("/tmp/Photos/Florida")
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 



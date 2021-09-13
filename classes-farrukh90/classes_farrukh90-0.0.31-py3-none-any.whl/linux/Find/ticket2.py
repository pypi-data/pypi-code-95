import sys
sys.path.append('../')
from Classes.shared_scripts.modules import *


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def taskchecker():
    filechecker("/mnt/secure")
    sizechecker("/mnt/secure")  
    filechecker("/etc/yum.repos.d/Media.repo.gz")

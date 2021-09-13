import sys
sys.path.append('../')
from Classes.shared_scripts.modules import *

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def taskchecker():
    filechecker("/tmp/fruits")
    sizechecker("/tmp/services")
    linechecker("/tmp/top10")
    linechecker("/tmp/bottom10")
    sizechecker("/tmp/sorted_fruits")
    filechecker("/tmp/sorted_fruits")

    sizechecker("/tmp/counted_services")
    filechecker("/tmp/counted_services")
    linetotalchecker("/tmp/counted_services", '1300')
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 

import os

# def search(dirname):
#     filenames = os.listdir(dirname)
#     for filename in filenames:
#         full_filename = os.path.join(dirname, filename)
#         print (full_filename)
#
# search("D:\SEANLAB6\git_algorithms\py_algorithms3\seanalgorithms3")

import os
alist=[]
for (path, dir, files) in os.walk("D:\SEANLAB6\git_algorithms\py_algorithms3\seanalgorithms3"):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        dirname=list(map(str,path.split('\\')))
        if dirname[-1] !="__pycache__" and dirname[-1] !="seanalgorithms3" and dirname[-1] !=".idea" :
            #print(dirname[-1])
            #print(dirname)
            if dirname[-1] not in alist :
                alist.append(dirname[-1])
                #print("  - [{}]({})".format(dirname[-1]))
        if ext == '.py' and filename[:-3]!="__init__" :
            if filename !="readfile.py":
                print("    - [{}]({}/{})".format(filename[:-3],dirname[-1],filename))
            #print("%s/%s" % (path, filename))

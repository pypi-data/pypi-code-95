# (1)   $export PATH=$PATH:$HOME/.local/bin
# (2)   $python3 setup.py sdist bdist_wheel
#
# run Twine to upload all of the archives under dist:
# (3)   $twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
#  if file HTTPError: 400 Client Error: File already exists.
#
#  Use this ******
# (3.1) $twine upload --skip-existing dist/*
# (4)   $sudo pip install mmWave -U
#
# if error: invalid command 'bdist_wheel'
# $pip3 install wheel
#
#
# vitalSign.py v0.0.8
#              v0.0.9
#              v0.0.10 :2020/02/04
#
# highAccuracy v0.0.4
#       v0.0.4 fix for Jetson nano
#
# peopleMB : v0.0.3
#           v0.0.4    :2019/12/06  fix for Jetson nano
#           v0.0.5    :2020/04/21  fix for Jetson nano
#
# srradar.py : v0.0.1 :2019/10/03
# v0.1.19 : add srradar.py
#
# people3D.py : v0.0.2 :2019/10/22
#               v0.0.3 :2019/10/23
#               v0.0.4 :2019/10/24
#
# pc3d.py     : v0.0.1 :2019/11/26
#               v0.0.2 :2019/11/27
#               v0.0.3 :2019/12/02
#
# pc3d_kv.py  : v0.0.1 :2019/11/25
#               v0.0.2 :2019/12/02
#
# lpdISK.py   : v0.0.1 :2019/12/04
#
# lpdISK_kv.py: v0.0.1 :2019/12/06
#
# vehicleOD.py   : v0.0.1 :2020/02/11
#
# trafficMD_kv.py :v0.0.2 :2020/03/18
# Original name: trafficMD.py :v0.0.1 :2020/03/18
#
# surfaceVD.py :v0.0.1 :2020/04/17
#
# trafficMD.py :v0.0.1 :2020/04/30
#               v0.1.0 :2021/04/21 add DataFrame output @v1.0.48
#
# droneRD.py   :v0.0.1 :2020/05/13
# droneRN.py   :v0.0.2 :2020/05/13 (change name from droneRD.py)
#
# pc3.py       :v0.0.1 :2020/06/19     added for v0.1.42
#               v0.1.1 :2021/04/21     add DataFrame output @v1.0.48
#               v0.1.2 :2021/05/06     add frameNumber and field change @v1.0.51
#               v0.1.3 :2021/05/06     revised dataframe dtype @v1.0.52
#
# zoneOD.py    :v0.0.1 :2020/07/21     added for v1.0.43 removed at v1.0.44
#
# vehicleODHeatMap.py :v0.0.1 :2020/07/21 add for v1.0.44
#
# vitalsign_kv.py :v0.0.1: 2020/10/20 
#
# vehicleODR.py :v0.0.1 :2021/01/07 v1.0.47
#
# roadwayTMD_kv :v0.1.0 :2021/04/21 @v1.0.49
#               :v0.1.1 :2020/05/02 @v1.0.50 add getRecordData(self,frameNum):
#                                                readFile(self,fileName):
#               :v0.1.2 :2020/05/04 @v1.0.51 bug fix
#
# pc3OVH        :v0.1.0 :2021/05/18
#               :v0.1.1 :2021/08/12
#
# lpdFDS        :v0.1.0 :2021/05/26 dataFrame/raw 
#               :v0.1.1 :2021/05/26 message change
#               :v0.1.2 :2021/05/26 bug fix
#
# trafficMD_I480.py :v0.1.0 :2021/09/16
#
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mmWave",
    version="0.1.59",
    author="Bighead Chen",
    author_email="zach_chen@joybien.com",
    description="Joybien mmWave (Batman-101/201/301/501) Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.joybien.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

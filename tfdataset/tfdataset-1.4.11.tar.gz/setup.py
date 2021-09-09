from setuptools import setup, find_packages
# import tfdataset

setup(
    name="tfdataset",
    version="1.4.11",
    description="Video To Images",
    author="Sang Pil Yoo, Vo Van Tu",
    author_email="ysp9714@gmail.com",
    url="",
    download_url="",
    install_requires=["opencv-python", 
                        "tqdm",
                        "numpy",
                        "grpcio",
                        "kazoo",
                        "bs4",
                        "pandas",
                        "tensorflow"],
    entry_points={"console_scripts": ["vidal=tfdataset.cutter:main",
                                      "actdata=tfdataset.action_recognition_data:main",
                                      "objdata=tfdataset.object_detection_data:main",]},
    packages=find_packages(exclude=["docs", "test*"]),
    package_data={'': ['eye_drop.json', 'glucometer.json', 'key.pem', 'star_inhandplus_com.crt']},
    keywords=["video", "frames"],
    python_requires=">=3.6",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)

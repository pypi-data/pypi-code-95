import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dicom2fem',
    version='2.0.0',
    description='Generation of finite element meshes from DICOM images',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/vlukes/dicom2fem',
    author='Vladimir Lukes',
    author_email='vlukes@kme.zcu.cz',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='fem dicom',
    packages=['dicom2fem'],
    include_package_data=True,
    package_data={'': ['*.png']}
)

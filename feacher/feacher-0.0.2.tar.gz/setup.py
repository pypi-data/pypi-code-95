from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'Feacher - An Image Feature Vector Extraction Library'
LONG_DESCRIPTION = 'A simple PyTorch based image feature extractor using Pre-Trained Models useful for Transfer Learning applications.'

setup(
        name="feacher", 
        version=VERSION,
        author="Hari Prasad",
        author_email="h4ri.prasad@gmail.com",
        url="https://github.com/qpochlabs/feacher",
        license="MIT",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            'torch',
            'Pillow',
            'torchvision',
        ],        
        keywords=['python', 'pytorch', 'torchvison', 'feature-extraction'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
            "Natural Language :: English",
        ]
)
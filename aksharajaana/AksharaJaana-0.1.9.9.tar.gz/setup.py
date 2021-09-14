import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AksharaJaana", 
    version="0.1.9.9",
    author="Navaneeth",
    author_email="navaneethsharma2310oct@gmail.com",
    description="Kannada OCR ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Navaneeth-Sharma/Akshara-Jaana/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
   install_requires=[
       "opencv-python >= 4.2.0.32",
       "numpy >= 1.18.4",
       "pdf2image==1.13.1",
       "pytesseract",
       "scikit-fuzzy",
   ],
)

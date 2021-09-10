import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "RELEASE.md").read_text()

setuptools.setup(
    name="fABBA",
    packages=['fABBA'],
    version="0.0.3",
    long_description=long_description,
    author="Stefan Guettel, Xinye Chen",
    author_email="stefan.guettel@manchester.ac.uk",
    description="An efficient aggregation based symbolic representation",
    long_description_content_type='text/markdown',
    url="https://github.com/nla-group/fABBA",
    # packages=setuptools.find_packages(),
    install_requires=['numpy', 'cv2'],
    license='BSD 3-Clause'
)
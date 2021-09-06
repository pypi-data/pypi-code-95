from setuptools import setup, find_packages
import codecs
import os

cdr = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(cdr, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


setup(
    name="Alert_Behavior",
    version = "1",
    author="Bishwa Sapkota",
    author_email= "bishowbs08@gmail.com",
    packages=["Alert_Behavior"],
    long_description_content_type="text/markdown",
    long_description=long_description,
    license= "MIT",
    install_requires =[
        "numpy ",
        "mediapipe ",
        "opencv-python",],


    )
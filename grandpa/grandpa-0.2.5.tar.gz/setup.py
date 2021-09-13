from distutils.core import setup


install_requires=[
   "setuptools",
    "wheel",
    "imageio",
    "numpy",
    "opencv-python-headless",
    "Pillow",
    "psutil"
]


setup(
    name='grandpa',
    version='0.2.5',
    packages=['grandpa', 'grandpa.utils'],
    url='https://dev.azure.com/matthiasrieger/ImageRecognition/_git/ir-graml-core',
    license='MIT License',
    author='Bizerba AI Team',
    author_email='pascal.iwohn@bizerba.com',
    description='',
    install_requires=install_requires,
    package_dir={"": "src"}
)

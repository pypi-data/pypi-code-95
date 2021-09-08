import setuptools

setuptools.setup(name="pykcode",
                 version="0.7.6",
                 author="piglite",
                 author_email="piglite@vip.sina.com",
                 description="kcode tutoring package",
                 long_description="kcode tutoring package built by piglite",
                 long_description_content_type="text/markdown",
                 url="https://github.com/piglite",
                 packages=setuptools.find_packages(),
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 python_requires='>=3.7',
                 py_modules=['codepen', 'codeai', 'codeqt', 'codeword'])

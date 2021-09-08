import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="JPSLInstructor",
    version="0.5.2",
    description="Install all modules for Jupyter Physical Science Lab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JupyterPhysSciLab/JPSLInstructor",
    author="Jonathan Gutow",
    author_email="gutow@uwosh.edu",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        # 'python>=3.6',
        'jupyter>=1.0.0',
        'jupyter-instructortools>=0.5.5',
        'jupyterPiDAQ>=0.7.3',
        'Algebra_with_SymPy>=0.9.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent'
    ]
)

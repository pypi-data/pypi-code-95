from setuptools import setup, find_namespace_packages
from glob import glob

setup(
    name='gutils',
    version='0.1.0',
    zip_safe=False,
    setup_requires=[],
    install_requires=[],
    dependency_links=[],
    use_scm_version=True,
    python_requires='~=3.7',
    package_dir={'': 'src'},
    include_package_data=True,
    url='https://github.com/MathieuTuli/gutils',
    packages=find_namespace_packages('src'),
    # DO NOT do tests_require; just call pytest or python -m pytest.
    license='License :: Other/Proprietary License',
    author='Mathieu Tuli',
    author_email='tuli.mathieu@gmail.com',
    description='Utility API for various python libraries',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
    ],
    scripts=glob('bin/*'),
)

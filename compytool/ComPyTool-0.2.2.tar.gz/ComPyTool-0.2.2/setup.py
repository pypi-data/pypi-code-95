from setuptools import find_packages, setup


setup(
    name='ComPyTool',
    version='0.2.2',
    description='A Python based tool to compare .bam and .vcf files using a SQLite3 database',
    author='Oliver Kutz',
    author_email='Oliver.Kutz@uniklinikum-dresden.de',
    url='https://github.com/KutzO/ComPy/',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ComPy = src.ComPyTool.__main__:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    package_dir={"": "src"},
    python_requires=">=3.6",
)

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BioCAT",
    version="0.9.6",
    author="D.N. Kononov, D.V. Krivonos",
    author_email="konanovdmitriy@gmail.com",
    description="NRP biosynthesis  Cluster  Analysis  Tool)",
    long_description="BioCAT",
    long_description_content_type="",
    url="https://github.com/DanilKrivonos/BioCAT",
    project_urls={
        "Bug Tracker": "https://github.com/DanilKrivonos/BioCAT",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    package_data={'BioCAT': ['BioCAT/example']},
    include_package_data=True,
    packages=['BioCAT', 'BioCAT.src', 'BioCAT.example', 'BioCAT.external', 'BioCAT.HMM', 'BioCAT.data'],
    install_requires=[
        'numpy>=1.21.0',
        'biopython>=1.79',
        'pandas>=1.2.5',
        'scikit-learn>=0.24.2'
    ],
    entry_points={
        'console_scripts': [
            'biocat=BioCAT:main'
        ]
    }
)

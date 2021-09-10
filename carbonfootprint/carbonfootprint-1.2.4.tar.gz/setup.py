import setuptools
import io
import os

# Meta-data
NAME = "carbonfootprint"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=NAME,
    version="1.2.4",
    author="Altanai",
    author_email="tara181989@gmail.com",
    description="carbon footprint of the power consumption by fuel mix. Calculates carbon footprint based on fuel mix and discharge profile at the utility selected. Can create graphs and tabular output for fuel mix based on input file of series of power drawn over a period of time.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renewable-energy-experiments/carbon-footprint-calculator",
    project_urls={
        "Bug Tracker": "https://github.com/renewable-energy-experiments/carbon-footprint-calculator/issues",
    },
    keywords=[
        'carbon-emission', 'energy-efficiency', 'utility-fuel-mix',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=['pandas'],
    # package_data={'carbonfootprint': ['dataset/carbon4.csv', 'dataset/north_west2020/*.csv']},
    # data_files=[('dataset', ['dataset/carbon4.csv'])],
    include_package_data=True,
    python_requires=">=3.6",
)

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FangEngine",
    version="0.0.2",
    author="CPSuperstore",
    author_email="cpsuperstoreinc@gmail.com",
    description="This engine allows you to easily create object oriented, event-driven games in Python! You can customize as much or as little of the engine as you need to build your next great game!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CPSuperstore/FangEngine",
    project_urls={
        "Bug Tracker": "https://github.com/CPSuperstore/FangEngineDocs/issues",
        "Documentation": "https://github.com/CPSuperstore/FangEngineDocs/wiki"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Topic :: Desktop Environment",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)

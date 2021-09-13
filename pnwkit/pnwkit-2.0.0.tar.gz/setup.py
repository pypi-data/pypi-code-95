from setuptools import setup

requirements = ["pnwkit-py"]

long_description_content_type = "text/markdown"
readme = ""
with open("README.md") as f:
    readme = f.read()
setup(
    name="pnwkit",
    author="Village",
    url="https://github.com/Village05/pnwkit-py",
    project_urls={
        "Documentation": "https://pnwkit-py.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/Village05/pnwkit-py/issues",
    },
    version="2.0.0",
    license="MIT",
    description="A Python wrapper for the Politics and War API.",
    long_description=readme,
    install_requires=requirements,
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    long_description_content_type=long_description_content_type,
)

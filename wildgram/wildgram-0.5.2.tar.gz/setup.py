import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wildgram",
    version="0.5.2",
    author="Grace Turner",
    author_email="gracekatherineturner@gmail.com",
    description="wildgram tokenizes and seperates tokens into ngrams of varying size based on the natural language breaks in the text.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/gracekatherineturner/wildgram",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

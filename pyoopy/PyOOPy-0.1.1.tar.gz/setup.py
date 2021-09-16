import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyOOPy',
    packages=['PyOOPy'],
    version='0.1.1',
    license='MIT',
    description='Object-oriented programming in Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Bartosz Paulewicz',
    author_email='podolce0@gmail.com',
    url='https://gitlab.com/baton96/PyOOP',
    download_url='https://gitlab.com/baton96/PyOOP/-/archive/0.1.1/PyOOP-0.1.1.tar.gz',
    keywords=['OOP', 'Object-oriented programming'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ]
)

import setuptools

setuptools.setup(
    name="joonmyung",
    version="0.0.4",
    author="JoonMyung Choi",
    author_email="pizard@korea.ac.kr",
    description="JoonMyung's Library",
    url="https://github.com/pizard/JoonMyung.git",
    license="MIT",
    py_modules=['joonmyung'],
    package=setuptools.find_packages(exclude = ['sample']),
    zip_safe=False,
    install_requires=[

    ]
)
# python setup.py sdist
# python setup.py bdist_wheel
# python -m twine upload dist/*
# ID:JoonmyungChoi
from setuptools import setup
setup(
    name='sheetsDB',
    version='0.0.2',
    packages=['sheetsDB'],
    author_email='fedor.tryfanau@gmail.com',
    zip_safe=False,
    install_requires=[
        "gspread",
        "oauth2client"
    ],
)
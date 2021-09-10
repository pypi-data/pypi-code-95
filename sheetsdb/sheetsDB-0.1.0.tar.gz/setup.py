from setuptools import setup
setup(
    name='sheetsDB',
    version='0.1.0',
    packages=['sheetsDB'],
    author_email='fedor.tryfanau@gmail.com',
    zip_safe=False,
    install_requires=[
        "gspread",
        "oauth2client"
    ],
)
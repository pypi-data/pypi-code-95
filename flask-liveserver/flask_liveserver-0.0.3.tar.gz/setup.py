from setuptools import setup, find_packages

setup(
    name="flask_liveserver",
    version="0.0.3",
    url="https://github.com/DevM63/flask_liveserver",
    author="m63#7150",
    author_email="jihonight@gmail.com",
    description="Live Server in Flask.",
    packages=["liveserver"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["watchdog", "flask", "flask-socketio"],
    zip_safe=False,
    classifiers=["License :: OSI Approved :: MIT License"]
)

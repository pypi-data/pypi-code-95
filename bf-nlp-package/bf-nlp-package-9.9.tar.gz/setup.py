import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Avoids IDE errors, but actual version is read from version.py
__version__ = None
with open("rasa/version.py") as f:
    exec(f.read())

# Get the long description from the README file
with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

tests_requires = [
    "pytest~=5.3.4",
    "pytest-cov~=2.8.1",
    "pytest-localserver~=0.5.0",
    "pytest-sanic~=1.6.0",
    "pytest-asyncio~=0.10.0",
    "pytest-xdist~=1.31.0",
    "responses~=0.10.9",
    "freezegun~=0.3.14",
    "nbsphinx>=0.5",
    "aioresponses~=0.6.2",
    "moto~=1.3.8",
    "fakeredis~=1.1.0",
    "mongomock~=3.18.0",
    "black~=19.10b0",
    "flake8~=3.7.9",
    "pytype~=2020.1.24",
    "google-cloud-storage~=1.25.0",
    "azure-storage-blob~=12.1.0",
    "coveralls~=1.11.0",
    "towncrier~=19.2.0",
    "nbsphinx>=0.5",
    "aioresponses~=0.6.2",
    "moto==1.3.8",
    "fakeredis~=1.1.0",
    "mongomock~=3.18.0",
    "black~=19.10b0",
    "flake8~=3.7.9",
    "pytype~=2020.1.24",
    "google-cloud-storage~=1.25.0",
    "azure-storage-blob~=12.1.0",
    "coveralls~=1.11.0",
    "towncrier~=19.2.0",
    "toml~=0.10.0",
    "semantic_version~=2.8.4",
    "sphinx==1.8.2",
    "sphinx-autobuild==0.7.1",
    "sphinxcontrib-programoutput==0.11",
    "pygments==2.2.0",
    "sphinxcontrib-httpdomain==1.6.1",
    "sphinxcontrib-websupport==1.1.0",
    "sphinxcontrib-trio==1.0.2",
    "sphinx-tabs==1.1.11",
    "sphinx-autodoc-typehints==1.6.0",
    "rasabaster~=0.7.23",
    
    
    
]

install_requires = [
    
    
    "requests>=2.23",
    "boto3~=1.12",
    "matplotlib~=3.1",
    "attrs>=19.3",
    "jsonpickle~=1.3",
    "redis~=3.4",
    "pymongo[tls,srv]~=3.8.0",
    "numpy~=1.16",
    "scipy~=1.4.1",
    "tensorflow==2.1.0",
    # absl is a tensorflow dependency, but produces double logging before 0.8
    # should be removed once tensorflow requires absl > 0.8 on its own
    "absl-py>=0.9",
    # setuptools comes from tensorboard requirement:
    # https://github.com/tensorflow/tensorboard/blob/1.14/tensorboard/pip_package/setup.py#L33
    "setuptools >= 41.0.0",
    "tensorflow-probability~=0.7",
    "tensor2tensor~=1.14.0",
    "apscheduler~=3.6",
    "tqdm~=4.31.0",
    "networkx~=2.4.0",
    "fbmessenger~=6.0.0",
    "pykwalify~=1.7.0",
    "coloredlogs~=10.0",
    "scikit-learn~=0.20.2",
    "ruamel.yaml~=0.15",
    "scikit-learn~=0.20.2",
    "slackclient~=2.0.0",
    "python-telegram-bot~=11.1",
    "twilio~=6.26",
    "webexteamssdk~=1.1",
    "mattermostwrapper~=2.0",
    "rocketchat_API~=0.6.0",
    "colorhash~=1.0",
    "pika~=1.1.0",
    "jsonschema~=3.2",
    "packaging~=19.0",
    "gevent~=1.4.0",
    "pytz~=2019.1",
    "python-dateutil~=2.8",
    "rasa-sdk~=1.8.0",
    "colorclass~=2.2",
    "terminaltables~=3.1.0",
    "sanic~=19.12.2",
    "sanic-cors==0.10.0b1",
    "sanic-jwt~=1.3.2",
    # needed because of https://github.com/huge-success/sanic/issues/1729
    "multidict==4.6.1",
    "aiohttp~=3.6",
    "questionary>=1.5.0",
    "python-socketio~=4.4",
    # the below can be unpinned when python-socketio pins >=3.9.3
    "python-engineio~=3.11",
    "pydot~=1.4",
    "async_generator~=1.10",
    "SQLAlchemy~=1.3.3",
    "sklearn-crfsuite~=0.3",
    "PyJWT~=1.7",
    # remove when tensorflow@1.15.x or a pre-release patch is released
    # https://github.com/tensorflow/tensorflow/issues/32319
    "gast==0.2.2",
    
]

extras_requires = {
    "test": tests_requires,
    
}


setup(
    name="bf-nlp-package",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        # supported python versions
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",
    packages=find_packages(exclude=["tests", "tools", "docs", "contrib"]),
    entry_points={"console_scripts": ["rasa=rasa.__main__:main"]},
    version="9.9",
    install_requires=install_requires,
    tests_require=tests_requires,
    extras_require=extras_requires,
    include_package_data=True,
    description="Open source machine learning framework to automate text- and "
    "voice-based conversations: NLU, dialogue management, connect to "
    "Slack, Facebook, and more - Create chatbots and voice assistants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Botsfactory",
    author_email="boutaina.j@gmail.com",
    maintainer="BF",
    maintainer_email="boutaina.j@gmail.com",
    license="Apache 2.0",
    keywords="nlp machine-learning machine-learning-library bot bots "
    "botkit rasa conversational-agents conversational-ai chatbot"
    "chatbot-framework bot-framework",
    url="https://botsfactory.com",
    download_url="https://gitlab.com/boutaina.jam/oncf_backend.git"
    "".format(__version__),
    project_urls={
        "Bug Reports": "https://gitlab.com/boutaina.jam/oncf_backend.git",
        "Source": "https://gitlab.com/boutaina.jam/oncf_backend.git",
    },
)

print("\nWelcome to BotsFactory")

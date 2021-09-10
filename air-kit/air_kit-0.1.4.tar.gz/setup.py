from setuptools import setup

with open("README.md", "r") as handle:
    long_description = handle.read()

# fmt: off
configuration = dict(
    name="air_kit",
    version="0.1.4",
    description="air's kit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
    ],
    author="air64",
    author_email="contact.air64@yandex.ru",
    maintainer=", ".join(
        (
            "air64 <contact.air64@yandex.ru>",
        ),
    ),
    maintainer_email="contact.air64@yandex.ru",
    url="https://gitlab.com/air64/air_kit",
    project_urls={
        "Gitlab": "https://gitlab.com/air64/air_kit",
    },
    license="MIT",
    packages=["air_kit"],
    python_requires=">=3.7",
    install_requires=[
        "python-dotenv==0.13.0",
        "pyyaml==5.3.1",
    ],
    extras_require={
        "telegram_bot": [
            "python-telegram-bot~=13.7",
        ],
    },
    include_package_data=True,
)
setup(**configuration)
# fmt: on

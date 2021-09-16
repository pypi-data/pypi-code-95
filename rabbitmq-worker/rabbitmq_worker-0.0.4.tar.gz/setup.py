from setuptools import find_packages, setup

setup(
    name="rabbitmq_worker",
    version="0.0.4",
    author="Enlaps Open Source",
    author_email="contact@enlaps.fr",
    description="Library to create simple rabbitmq workers resilient to connection/channel shutdown and simple producers.",
    url="https://gitlab.com/enlaps-public/web/rabbitmq-worker",
    install_requires=["pika>=1.2.0"],
    packages=find_packages(),
    extras_require={"dev": ["pytest", "mypy", "pylint"]},
    python_requires=">=3.6",
)

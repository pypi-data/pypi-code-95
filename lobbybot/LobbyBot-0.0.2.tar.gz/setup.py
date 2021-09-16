import setuptools

name = 'LobbyBot'


setuptools.setup(
    name=name,
    version="0.0.2",
    author="Pirxcy",
    description="24/7 Fortnite Lobbybot With Online Dashboard",
    long_description="24/7 Fortnite Lobbybot With Online Dashboard",
    long_description_content_type="text/markdown",
    url="https://github.com/PirxcyFinal/pirxcybotv2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'sanic',
        'fortnitepy',
        'BenBotAsync',
        'PirxcyPinger'
    ],
)

from setuptools import setup, find_packages

setup(
    name="static_data_dp",
    packages=find_packages(),
    version="0.1.1",
    description="Library to easily handles ddragon ressources files for League of Legends, origined by Canisback, modified by dp0973",
    author="dp0973",
    author_email="yeong0973@gmail.com",
    url="https://github.com/dp0973/static-data",
    keywords=["Riot API", "python", "static-data"],
    classifiers=[],
    install_requires=["requests", "asyncio", "aiohttp"],
)

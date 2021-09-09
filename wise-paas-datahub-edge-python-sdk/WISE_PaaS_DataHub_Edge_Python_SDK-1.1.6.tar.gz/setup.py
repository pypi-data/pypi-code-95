import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="WISE_PaaS_DataHub_Edge_Python_SDK",
    version="1.1.6",
    author="Steven Li",
    author_email="StevenHY.Li@advantech.com.tw",
    description="WISEPaaS_DataHub_Edge_Python_SDK package allows developers to write Python applications which access the WISE-PaaS/DataHub Platform via MQTT or MQTT over the secure webSocket protocol.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/advwacloud/WISEPaaS.DataHub.Edge.Python.SDK",
    packages=setuptools.find_packages(),
    install_requires=[
        "paho-mqtt==1.4.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
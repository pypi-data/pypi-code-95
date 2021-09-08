import setuptools

setuptools.setup(
    name         = "ddgcli",
    version      = "0.2",
    author       = "x93bd",
    author_email = "edkz@nogafam.me",
    description  = "A ddg unnoficcial cli",
    license      = "GPL 3",
    keywords     = ["duckduckgo", "cli"],
    url          = "https://github.com/borisd93/ddgcli",
    packages     = ["ddgcli"],
    scripts      = ["ddgcli/main.py"],
    entry_points = {
        "console_scripts": ["ddgcli=ddgcli.main:ddgcli"]
    },
    classifiers  = [
        "Development Status :: 3 - Alpha",
    ],
    install_requires = ["user_agent", "requests", "click"]
)

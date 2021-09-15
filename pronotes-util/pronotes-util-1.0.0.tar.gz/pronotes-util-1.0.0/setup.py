from setuptools import setup
from setuptools.command.install import install as install


class CustomInstall(install):
    def run(self):
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        install.run(self)


setup(
    name="pronotes-util",
    version = '1.0.0',
    author="Praful Mohanan",
    description = "Helper package for downloading nltk static data on the go",
    install_requires = [
        'nltk'
    ],
    setup_requires = [
        'nltk'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],    
    python_requires='>=3.6',
    cmdclass={'install': CustomInstall},
   )

# --extra-index-url https://testpypi.python.org/pypi
# Django==1.7.7
# django-stackexchange-feed==0.4
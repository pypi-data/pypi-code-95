from setuptools import setup, find_packages, version

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name="voice_comm",
    version="0.0.3",
    description="With this package you can create programs which can speak to you and recognize your voice adn run commands. (easy eg.: You can create J.A.R.V.I.S from Iron Man :))",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    author='Da4ndo',
    author_email = 'vrgdnl20@gmail.com',
    License="MIT",
    classifiers=classifiers,
    keywords=['voice_comm', 'voice comm', 'voice_comm', 'Voice Communication', 'voice communication'],
    packages=find_packages(),
    install_requires=['pyttsx3', 'SpeechRecognition']
)
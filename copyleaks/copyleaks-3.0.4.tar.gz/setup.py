from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='copyleaks',
    packages=['copyleaks', 'copyleaks.exceptions', 'copyleaks.models', 'copyleaks.models.submit', 'copyleaks.models.submit.properties'],
    version='3.0.4',
    description='Copyleaks API gives you access to a variety of plagiarism detection technologies to protect your online content. Get the most comprehensive plagiarism report for your content that is easy to use and integrate.',
    author='Copyleaks ltd',
    author_email='sales@copyleaks.com',
    url='https://api.copyleaks.com',
    download_url='https://github.com/Copyleaks/Python-Plagiarism-Checker',
    keywords=['copyleaks', 'api', 'plagiarism', 'content', 'checker', 'online', 'academic', 'publishers', 'websites'],
    install_requires=[
        'requests', 'python-dateutil', 'pytz'
    ],
    classifiers=[],
)

import os
import re
import setuptools


def get_version():
    with open("gitlab_job_exec/__init__.py", "r") as version_file:
        for line in version_file:
            if line.startswith("__version__"):
                return re.search('"(.*)"', line)[1] + "." + os.environ.get("CI_PIPELINE_IID")
    return None


def get_requirements():
    requirements = []
    with open("requirements.txt", "r") as requirement_file:
        for line in requirement_file:
            if not line.startswith("#"):
                requirements.append(line.strip())
    return requirements


with open("README.md", "r") as fh:
    long_description = fh.read()    # pylint: disable=invalid-name

setuptools.setup(
    name="gitlab-job-exec",
    version=get_version(),
    author="Uncrns",
    author_email="uncrns.devs@gmail.com",
    description="Execute GitLab-CI docker jobs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=os.environ.get("CI_PROJECT_URL"),
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        ],
    python_requires=">=3.6",
    install_requires=get_requirements(),
    entry_points={'console_scripts': ['gitlab-job-exec = gitlab_job_exec.cli:main']},
    )

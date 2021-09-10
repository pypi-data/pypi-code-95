from setuptools import find_packages, setup


def readme():
  with open('README.md') as f:
    return f.read()


def requirements():
  with open('requirements.txt') as f:
    return f.read()


setup(name='algo_crawler',
      version='v0.0.2',
      description="Crawl algorithm problems from any website",
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://github.com/SeanHwangG/algo-crawler',
      author='Sean Hwang',
      author_email='rbtmd1010@gmail.com',
      packages=find_packages(),
      python_requires='>=3.8',
      install_requires=requirements(),
      license='MIT')

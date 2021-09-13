from setuptools import setup

setup(
    name='odoo-core-install-generator',
    version='1.0.3',
    description='Odoo core install generator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/is4res/odoo-core-install-generator',
    license='MIT',
    author='Biszx',
    author_email='isares.br@gmail.com',
    scripts=['scripts/odoo-core-install-generator'],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)

from setuptools import setup, find_packages
import os


def package_files(directory):
    paths = []
    for (path, _directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


extra_files = package_files('tinybird/templates') + package_files('tinybird/static') + \
    package_files('tinybird/default_tables') + package_files('tinybird/default_pipes') + \
    package_files('tinybird/sql')


setup(
    name='tinybird',
    version='1.0',
    description='tinybird',
    long_description='tinybird analytics',
    long_description_content_type='text/markdown',
    author='tinybird.co',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=[
        'basictracer==3.1.0',
        'cachetools==4.0.0',
        'click==7.0',
        'clickhouse-driver==0.2.0',
        'clickhouse-toolset==0.11.dev0',
        'datasketch==1.2.10',
        'confluent-kafka==1.7.0',
        'cryptography==3.3.2',
        'fastavro==1.4.1',
        'humanfriendly==8.2',
        'Markdown==3.2.1',
        'numpy==1.21.2',
        'passlib==1.7.1',
        'psutil==5.6.3',
        'psycopg2-binary==2.8.5',
        'pycurl==7.43.0.6',
        'pyjwt[crypto]==1.6.4',
        'rangehttpserver==1.2.0',
        'redis==3.2.1',
        'requests==2.25.1',
        'requests-toolbelt==0.9.1',
        'streaming-form-data==1.1.0',
        'tabulate==0.8.3',
        'toposort==1.5',
        'torngithub==0.2.0',
        'tornado==5.1.1',
        'opentracing==2.0',
        'tornado-opentracing==1.0.1',
        'msal==1.5.0',
        'wheel',
        'lz4',
        'python-snappy',
        'cffi==1.14.5',
        'aiohttp==3.7.4.post0',
    ],
    package_dir={'tinybird': 'tinybird/'},
    package_data={
        # 'tinybird': ['../templates/*', '../static/*']
        'tinybird': extra_files
    },
    setup_requires=[
        'pytest-runner',
        'cffi==1.14.5'
    ],
    cffi_modules=["tinybird/fast_rowbinary_build.py:ffibuilder"],  # "filename:global"
    extras_require={
        'test': [
            'pytest==4.6',
            'pytest-cov',
            'flake8==3.9.2',
            'flake8-bugbear',
            'pytest-env==0.6.2',
            'urllib3<1.25.10,>=1.25.4',
            'gsutil==4.59',
            'google-api-python-client==2.0.2',
            'google-auth==1.27.1',
            'google-auth-httplib2==0.1.0',
            'google-cloud-storage==1.36.2',
            'google-cloud-bigquery==2.11.0',
            'snowflake-connector-python==2.3.8',
            'oauth2client==3.0.0',
            'pytest-parallel==0.1.0',
        ],
        'deploy': [
            'google-auth==1.7.0',
            'PyYAML==5.1',
        ],
        'doc': [
            'sphinx==3.3.1',
            'sphinx-autobuild==0.7.1',
            'Pallets-Sphinx-Themes',
            'sphinxcontrib-httpdomain'
        ],
        'devtools': [
            'matplotlib',
            'memory_profiler',
            'flameprof',
            'rope'
        ]
    },
    entry_points={
        'console_scripts': [
            'tinybird_server=tinybird.app:run',
            'tinybird_tool=tinybird.cli:cli',
            'tb=tinybird.tb_cli:cli',
        ],
    }
)

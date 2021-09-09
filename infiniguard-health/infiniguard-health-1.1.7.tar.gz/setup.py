
SETUP_INFO = dict(
    name = 'infiniguard-health',
    version = '1.1.7',
    author = 'Maxim Kigel',
    author_email = 'mkigel@infinidat.com',

    url = None,
    license = 'BSD',
    description = """infiniguard-health""",
    long_description = """infiniguard-health""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'arrow>=0.15.7',
'bs4',
'capacity>=1.3.14',
'dmidecode',
'freezegun',
'iba-install',
'infi.caching>=0.0.2',
'infi.storagemodel>=0.4.33',
'infinisdk>=173.0.0',
'munch>=2.5.0',
'netifaces>=0.10.9',
'ntplib',
'parameterized>=0.7.4',
'pygments',
'psutil',
'represent>=1.6.0',
'retrying',
'schematics==1.1.0.1',
'setuptools',
'structlog',
'tenacity>=6.2.0',
'wrapt',
'xmltodict>=0.12.0'
],
    namespace_packages = [],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['health_monitor = infiniguard_health.health_monitor.health_monitor_service:main_loop',
'failover_cli = infiniguard_health.cli_tools.cli_tool:run_failover_cli',
'health_cli = infiniguard_health.cli_tools.cli_tool:run_regular_cli',
'debug_cli = infiniguard_health.cli_tools.cli_tool:run_debug_cli',
'rpm_post_install = infiniguard_health.scripts.rpm_helpers:post_install',
'rpm_pre_uninstall = infiniguard_health.scripts.rpm_helpers:pre_uninstall'],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()


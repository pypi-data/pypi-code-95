import setuptools, os

readme_path = 'README.md'

if os.path.exists(readme_path):
    with open(readme_path, "r") as f:
        long_description = f.read()
else:
    long_description = 'kcliutils'

setuptools.setup(
    name="kcliutils",
    version="0.1.12",
    author="Kristof",
    description="kcliutils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kkristof200/py_cli_utils",
    packages=setuptools.find_packages(),
    install_requires=[
        'bullet>=2.2.0',
        'jsoncodable>=0.1.7',
        'kcu>=0.0.68',
        'kdependencies>=0.0.4'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            # Package related

            'new_python_package=kcliutils.__main__:new_package',
            'npp=kcliutils.__main__:new_package',

            'upgrade_python_package=kcliutils.__main__:upgrade',
            'upp=kcliutils.__main__:upgrade',

            'publish_python_package=kcliutils.__main__:publish',
            'ppp=kcliutils.__main__:publish',

            'publish_and_push_python_package=kcliutils.__main__:publish_and_push',
            'pipush=kcliutils.__main__:publish_and_push',

            'upgrade_push_install=kcliutils.__main__:upgrade_push_install',
            'prpipush=kcliutils.__main__:upgrade_push_install',


            # Formatting

            'clean_lines=kcliutils.__main__:clean_lines',
            'cl=kcliutils.__main__:clean_lines',

            'migrate_comment_line_len=kcliutils.__main__:migrate_comment_line_len',


            # Git

            'push=kcliutils.__main__:push',
            'psh=kcliutils.__main__:push',

            'fetch=kcliutils.__main__:fetch',
            'ftch=kcliutils.__main__:fetch',

            'pull=kcliutils.__main__:pull',
            'pll=kcliutils.__main__:pull',


            # Pip

            'pip_uninstall=kcliutils.__main__:uninstall',
            'pipu=kcliutils.__main__:uninstall',

            'pip_install=kcliutils.__main__:install',
            'pipi=kcliutils.__main__:install',
            'pipiu=kcliutils.__main__:install',

            'pip_reinstall=kcliutils.__main__:reinstall',
            'pipir=kcliutils.__main__:reinstall',


            # New files

            'python_requirements=kcliutils.__main__:create_requirements_file',
            'pyreqs=kcliutils.__main__:create_requirements_file',

            'create_python_install_file=kcliutils.__main__:create_install_file',
            'pif=kcliutils.__main__:create_install_file',

            'new_python_api=kcliutils.__main__:create_new_api',
            'npa=kcliutils.__main__:create_new_api',

            'new_python_class=kcliutils.__main__:create_new_class',
            'npc=kcliutils.__main__:create_new_class',

            'new_python_class_from_json=kcliutils.__main__:create_class_from_json',
            'npcj=kcliutils.__main__:create_class_from_json',

            'new_python_enum=kcliutils.__main__:create_new_enum',
            'npe=kcliutils.__main__:create_new_enum',

            'new_python_file=kcliutils.__main__:create_new_file',
            'npf=kcliutils.__main__:create_new_file',

            'new_python_flow=kcliutils.__main__:create_new_flow',
            'npfl=kcliutils.__main__:create_new_flow',

            'new_python_subpackage=kcliutils.__main__:create_new_subpackage',
            'nps=kcliutils.__main__:create_new_subpackage'
        ]
    },
    python_requires='>=3.4',
)
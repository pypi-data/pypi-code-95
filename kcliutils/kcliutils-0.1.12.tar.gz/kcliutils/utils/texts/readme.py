# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, List
import os

# Pip
from kdependencies import InstalledPackage
from kcu import strings

# Local
from .core_texts import readme
from .utils import multi_replace
from .file_key import FileKey
from .all_file_consts import AllFileConsts

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- Public methods -------------------------------------------------------- #

def updated_readme(
    readme: str,
    demo: Optional[str],
    dependencies: Optional[List[InstalledPackage]]
) -> str:
    if demo:
        usage = strings.between(readme, '## Usage', '##')

        if usage:
            readme = readme.replace(usage.strip(), '~~~~python\n{}\n~~~~'.format(demo.strip()))

    if dependencies:
        old_dependencies = strings.between(readme, '## Dependencies', '##')

        if not old_dependencies:
            if readme.endswith('## Dependencies'):
                old_dependencies = '## Dependencies'
        else:
            old_dependencies = '## Dependencies' + old_dependencies

        if old_dependencies:
            readme = readme.replace(
                old_dependencies.strip(),
                '## Dependencies\n\n' + ', '.join(
                    ['[{}]({})'.format(
                        d.name if not d.private else d.home_url.split(os.sep)[-1], 'https://pypi.org/project/{}'.format(d.name) if not d.private else d.home_url)
                        for d in dependencies
                    ]
                )
            )

    return readme.strip()

def new_readme(
    package_name: str,
    full_repo_name: Optional[str] = None,
    description: Optional[str] = None,
    dependencies: Optional[List[InstalledPackage]] = None
) -> str:
    return multi_replace(
        readme,
        keys_vals={
            FileKey.PACKAGE_NAME: package_name,
            FileKey.SHIELDS: __create_shields(package_name, full_repo_name) if full_repo_name else '',
            FileKey.DESCRIPTION: description or '',
            FileKey.DEPENDENCIES: ', '.join(
                ['[{}]({})'.format(
                    d.name if not d.private else d.home_url.split(os.sep)[-1], 'https://pypi.org/project/{}'.format(d.name) if not d.private else d.home_url)
                    for d in dependencies
                ]
            ) if dependencies else ''
        },
        file_consts=AllFileConsts.PY.value
    )


# -------------------------------------------------------- Private methods ------------------------------------------------------- #

def __create_shields(
    package_name: str,
    full_repo_name: Optional[int]
):

    return '\n\n'.join(
        [
            '\n'.join(
                [
                    __shield('PyPI - package version', 'pypi/v/{}?logo=pypi'.format(package_name)),
                    __shield('PyPI - license', 'pypi/l/{}?label=package%20license'.format(package_name)),
                    __shield('PyPI - python version', 'pypi/pyversions/{}?logo=pypi'.format(package_name)),
                    __shield('PyPI - downloads', 'pypi/dm/{}?logo=pypi'.format(package_name))
                ]
            ),
            '\n'.join(
                [
                    __shield('GitHub - last commit', 'github/last-commit/{}'.format(full_repo_name)),
                    __shield('GitHub - commit activity', 'github/commit-activity/m/{}'.format(full_repo_name))
                ]
            ),
            '\n'.join(
                [
                    __shield('GitHub - code size in bytes', 'github/languages/code-size/{}'.format(full_repo_name)),
                    __shield('GitHub - repo size', 'github/repo-size/{}'.format(full_repo_name)),
                    __shield('GitHub - lines of code', 'tokei/lines/github/{}'.format(full_repo_name)),
                ]
            ),
            __shield('GitHub - license', 'github/license/{}?label=repo%20license'.format(full_repo_name))
        ]
    )

def __shield(name: str, url_data: str, style: str = 'flat-square') -> str:
    return '![{}](https://img.shields.io/{}{}style={})'.format(name, url_data, '&' if '?' in url_data else '?', style)


# -------------------------------------------------------------------------------------------------------------------------------- #
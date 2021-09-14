from pathlib import Path

from glabpkg.version import __version__
from pkglts.local import pkg_full_name
from pkglts.option.doc import fmt_badge
from pkglts.option_object import Option


class OptionGlabPkg(Option):
    def version(self):
        return __version__

    def root_dir(self):
        return Path(__file__).parent

    def update_parameters(self, cfg):
        cfg['base']['authors'] = [('revesansparole', 'revesansparole@gmail.com')]

        for ext in [".csv", ".ini", ".json", ".rst", ".svg"]:
            if ext not in cfg['data']['filetype']:
                cfg['data']['filetype'].append(ext)
        cfg['data']['use_ext_dir'] = False

        cfg['doc']['fmt'] = "rst"

        cfg['pysetup']['intended_versions'] = ["39"]

        cfg['sphinx']['theme'] = "sphinx_rtd_theme"
        cfg['sphinx']['gallery'] = "example"

        cfg['test']['suite_name'] = "pytest"

        cfg['gitlab']['server'] = "gitlab.com"

        # add a parameter to the option
        return super().update_parameters(cfg)

    def check(self, cfg):
        invalid_params = []

        return invalid_params

    def require_option(self, cfg):
        return ['glabbase', 'pysetup', 'sphinx', 'coverage', 'pypi', 'conda', 'data']

    def environment_extensions(self, cfg):
        if "/" in cfg['gitlab']['owner']:
            gr = cfg['gitlab']['owner'].split("/")
            group_owner = gr[0]
            subgroup_owner = "/".join(gr[1:]) + "/"
        else:
            group_owner = cfg['gitlab']['owner']
            subgroup_owner = ""

        pages_url = f"https://{group_owner}.gitlab.io/{subgroup_owner}{cfg['gitlab']['project']}/"
        # documentation
        url = pages_url
        img = f"{pages_url}_images/badge_doc.svg"
        badge_doc = fmt_badge(img, url, "Documentation status", cfg['doc']['fmt'])
        # pip
        ver = cfg['version']
        url = (f"https://pypi.org/project/{cfg['gitlab']['project']}"
               f"/{ver['major']:d}.{ver['minor']:d}.{ver['post']:d}/")
        img = f"{pages_url}_images/badge_pkging_pip.svg"
        badge_pip = fmt_badge(img, url, "PyPI version", cfg['doc']['fmt'])
        # conda
        url = f"https://anaconda.org/revesansparole/{pkg_full_name(cfg)}"
        img = f"{pages_url}_images/badge_pkging_conda.svg"
        badge_conda = fmt_badge(img, url, "Conda version", cfg['doc']['fmt'])

        return {"badges": [badge_doc, badge_pip, badge_conda]}

import re
import yaml
import requests
from ratelimit import limits, sleep_and_retry
from markdown import Extension
from markdown.preprocessors import Preprocessor

from requests.exceptions import HTTPError


class CiteprocConversionError(Exception):
    pass


@sleep_and_retry
@limits(calls=5, period=1)
def format_bibliography(csl_yaml, citation_style, citeproc_endpoint=None):
    """
    POST request to CITEPROC_ENDPOINT to format csl_yaml as a bibliography in
    CITATION_STYLE.
    """

    if not citeproc_endpoint:
        raise ValueError('No citeproc endpoint defined')

    r = requests.post(
        citeproc_endpoint,
        json={'items': csl_yaml},
        params={
            'style': citation_style,
            'responseformat': 'html'
        }
    )

    try:
        r.raise_for_status()
    except HTTPError:
        raise CiteprocConversionError(
            f'Citeproc endpoint returned HTTP {r.status_code} error: '
            + r.content.decode()
        )

    return r.content.decode()


class CSLYAMLPreprocessor(Preprocessor):

    RE_CSL_YAML = re.compile(
        r'''
            (?P<fence>^(?:~{3,}|`{3,}))[ ]*     # opening fence
            bibl
            \n                                  # newline (end of opening fence)
            (?P<csl_yaml>.*?)(?<=\n)            # the CSL YAML block
            (?P=fence)[ ]*$                     # closing fence
        ''',
        flags=re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def __init__(self, md, configs, **kwargs):
        super().__init__(md)
        self.configs = configs

    def _add_to_stash(self, m):
        csl_yaml = yaml.load(m['csl_yaml'], Loader=yaml.FullLoader)
        styled_bibl = format_bibliography(
            csl_yaml, citation_style=self.configs['citation_style'],
            citeproc_endpoint=self.configs['citeproc_endpoint']
        )
        placeholder = self.md.htmlStash.store(styled_bibl)
        return placeholder

    def run(self, lines):
        text = '\n'.join(lines)
        text = self.RE_CSL_YAML.sub(self._add_to_stash, text)
        return text.split('\n')


class CiteprocExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'citeproc_endpoint': [
                '', 'Citeproc endpoint where the HTTP requests will go'
            ],
            'citation_style': [
                'chicago-author-date',
                'Citation style that the bibliographies will be converted into.'
            ]
        }
        Extension.__init__(self, **kwargs)

    def extendMarkdown(self, md):
        configs = self.getConfigs()
        if not configs['citeproc_endpoint']:
            print(
                'Warning: no citeproc_endpoint is defined in the citeproc '
                'extension config, hence the processors will not be registered.'
            )
        else:
            md.registerExtension(self)
            md.preprocessors.register(
                CSLYAMLPreprocessor(md, configs),
                'csl_yaml', 26  # Before FencedBlockPreprocessor
            )

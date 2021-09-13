"""This XBlock provides syntax highlighting via the PrismJS library"""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Scope, String, Integer
from xblockutils.resources import ResourceLoader

class PrismXBlock(XBlock):
    """
    Provide syntax highlighting within a code editor 
    """

    xblock_loader = ResourceLoader(__name__)

    display_name = String(
        help="The display name for this component",
        default="Syntax Highlighter",
        scope=Scope.settings
    )

    code_data = String(
        help="Code contents to display within editor",
        default="print('hello world')",
        scope=Scope.content
    )
    MAXHEIGHT_HELP = "Maximum height of code block (px)"

    maxheight = Integer(
        help=MAXHEIGHT_HELP,
        default=450,
        scope=Scope.settings
    )

    LANGUAGE_CHOICES = [
        {'display_name': 'Bash', 'value': 'bash'},
        {'display_name': 'C-like', 'value': 'clike'},
        {'display_name': 'CSS', 'value': 'css'},
        {'display_name': 'Go', 'value': 'go'},
        {'display_name': 'Java', 'value': 'java'},
        {'display_name': 'Javascript', 'value': 'javascript'},
        {'display_name': 'JSON', 'value': 'json'},
        {'display_name': 'Lua', 'value': 'lua'},
        {'display_name': 'Markup', 'value': 'markup'},
        {'display_name': 'Python', 'value': 'python'},
        {'display_name': 'Ruby', 'value': 'ruby'},
        {'display_name': 'Shell-Session', 'value': 'shell-session'},
        {'display_name': 'SQL', 'value': 'sql'},
        {'display_name': 'YAML', 'value': 'yaml'},
    ]

    LANGUAGE_HELP = "Select a programming language"

    language = String(
        help=LANGUAGE_HELP,
        default='python',
        values=LANGUAGE_CHOICES,
        scope=Scope.settings
    )

    THEME_CHOICES = [
        {'display_name': 'Light', 'value': 'light'},
        {'display_name': 'Dark', 'value': 'dark'},
    ]

    THEME_HELP = "Select a syntax highlighting theme"
    
    theme = String(
        help= THEME_HELP,
        default="dark",
        values=THEME_CHOICES,
        scope=Scope.settings
    )


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        Return a fragment that contains the editor with code for student view.
        """
        frag = Fragment()
        frag.add_content(self.xblock_loader.render_django_template(
            'static/html/lms.html', 
            context={'self':self}
        ))

        css_path  = "static/css/{}.css".format(self.theme)
        frag.add_css(self.resource_string(css_path))
        frag.add_css(self.resource_string("static/css/prism.css"))
        frag.add_javascript(self.resource_string("static/js/src/prism.js"))
        frag.initialize_js('RunPrism')
        return frag

    def studio_view(self, context=None):
        """
        Return a fragment that contains the editor with code for studio view.
        """
        frag = Fragment()
        frag.add_content(self.xblock_loader.render_django_template(
            'static/html/studio.html', 
            context={'self':self}
        ))

        css_path  = "static/css/{}.css".format(self.theme)

        frag.add_css(self.resource_string("static/codemirror/codemirror.css"))
        frag.add_css(self.resource_string(css_path))

        frag.add_javascript(self.resource_string("static/js/src/studio.js"))
        frag.add_javascript(self.resource_string("static/codemirror/codemirror.js"))
        frag.add_javascript(self.resource_string("static/js/src/prism.js"))
        frag.initialize_js('PrismXBlock')
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Update saved code input with new code input
        """
        self.display_name = data.get('display_name')
        self.code_data = data.get('code_data')
        self.language = data.get('language')
        self.theme = data.get('theme')
        self.maxheight = data.get('maxheight')
        return {'result': 'success'}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("PrismXBlock",
             """<prism/>
             """),
            ("Multiple PrismXBlock",
             """<vertical_demo>
                <prism/>
                <prism/>
                <prism/>
                </vertical_demo>
             """),
        ]

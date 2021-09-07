from browser import document

from kirui.vdom import minify


class MinifyTest:
    def test_minify_text_content(self):
        el = document.createElement('DIV')
        el.innerHTML = """
            <span style="font-weight: bold">
                text
            </span>
            sdfsdfsdf
        """

        assert el.innerHTML != """<span style="font-weight: bold">text </span>sdfsdfsdf  """
        minify(el)
        assert el.innerHTML.strip() == """<span style="font-weight: bold">text </span>sdfsdfsdf"""

"""
Base class for tests. Primarily provides Markdown Outputs.
"""

from IPython.display import display, Markdown

class BaseTest:
    
    def printout(self, outcome, test_name):
        if outcome:
            markdown = Markdown(f"""**{test_name}:** ✅""")
        else:
            markdown = Markdown(f"""**{test_name}:** ❌""")
        display(markdown)
            
    def print_results(self, key, test, *args, main=False, output=False):
        if main and output:
            result = test(self, True)
        elif main:
            result = test(self)
        else:
            result = test(*args)
        if output:
            markdown = Markdown(f"**{key}:** {result}")
            display(markdown)
        else:
            self.printout(result, key)
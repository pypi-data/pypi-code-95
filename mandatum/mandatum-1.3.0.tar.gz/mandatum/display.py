from rich.console import Console


console = Console()


class Display():
    """Display Class"""
    def __init__(self):
        """
        Display class to display and print stuff on the console/terminal.
        """
        self.text = None
        self.style = None
        self.justify = None

    def print(self, text="", style="", justify=""):
        """
        Prints text on the terminal

        Parameters:
        `text`:Text to display
        `style`:Styling the text like `bold red`
        `justify`:aligning the text on some side eg. `center`, `left` etc.
        """

        self.text = text
        self.style = style
        self.justify = justify
        
        console.print(
            self.text,
            style=self.style,
            justify=self.justify,
        )
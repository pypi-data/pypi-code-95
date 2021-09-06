# Importings
from rich.console import Console

# Initial setup
console = Console()


# Prompt Class
class Prompt():
    """Prompt Class"""
    def __init__(self, color="red", bold_text=True):
        """
        Used for taking input

        Parameters:
        `color`:Color of the prompt
        `bold_text`:Asks if bold text is required or not
        """
        
        # Color for input text
        self.color = color

        # text bold
        self.bold_text = bold_text
        self.bold_style = ""

        # If bold text is required
        if self.bold_text == True:
            self.bold_style = "bold "
        
        # If not
        else:
            self.bold_style = ""

    def change_color(self, color="red"):
        """
        Chages the default color
        `color`:New color for the prompt

        """
        self.color = color
        return True

    # Main prompt for input
    def input(self, text):
        """
        Takes input from the user
        `text`: text to be displayed while taking input 
        """

        # Printing prompt
        console.print(
            text, style=f"{self.bold_style}{self.color}", end=""
        )

        # Asking for user input
        self.inp = input()

        # Returning user input
        return self.inp

    def change_bold_text(self, bold_text=False):
        """Changes bold text"""
        self.bold_text = bold_text

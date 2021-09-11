# Importings
from rich.console import Console
from .prompt import Prompt
import sys

# Initial Setup
console = Console()


# Mode Class
class Mode():
    """Mode class"""
    def __init__(self, name="", description="", theme=["red", "green"], bold_text=False):
        """
        Creates different modes in the application, Paramters are set as default

        Parameters:
        `name`:Name of the mode
        `description`:Description of the mode
        `theme`:theme for the mode example : ["red","green"]
        `bold_text`:Asks if bold text is required
        """
        self.name = name

        # Description
        self.description = description

        # Theme
        self.theme = theme

        # Text Bold
        self.bold_text = bold_text
        self.bold_style = ""

        # If bold text
        if self.bold_text:
            self.bold_style = "bold "
        
        # If not
        else:
            self.bold_style = ""

        # Spacing on both sides of name of mode for text display on screen
        self.spacing = 4

        # Prompt for mode
        self.prompt = None





    def config_name_space(self, space=4):
        """configures space on both sides of mode name"""
        self.spacing = space
    




    def init_prompt(self):
        """
        Initializes prompt for the menu with the same theme as the mode
        """
        # Initializing prompt
        self.prompt = Prompt(color=self.theme[0], bold_text=self.bold_text)
        
        return True






    def change_prompt_color(self, color=""):
        try:
            # Changing Prompt Color
            self.prompt.color = color
        
        except:
            # Giving Warning
            console.print("Make sure you have initialized prompt.", style="bold red")
            sys.exit()
            




    def change_bold_text(self, bold_text=False):
        # Changing bold text
        self.bold_text = bold_text







    def get_name(self):
        """Return mode name"""
        # Return mode name
        return self.name





    def get_name_space(self):
        # Return mode name with space on both sides
        _space = " "
        # Looking For errors
        try:
            return f"{_space*self.spacing}{self.name}{_space*self.spacing}"
        # Asking developer to fix errors
        except:
            console.print(
                "\nMake sure you have added a valid number for text spacing.\n", style="bold red"
            )
            exit()





    def get_description(self):
        """returns mode description"""
        return self.description
    





    def change_description(self, description=""):
        """Changes mode description"""
        self.description = description
    




    def get_theme(self):
        """returns mode theme"""
        return self.theme





    def change_theme(self, theme=["red", "green"]):
        """Changing Mode Theme"""
        self.theme = theme
        





    def print_details(self):
        """prints mode details"""
        
        # Mode name
        console.print(
            self.get_name_space(), style=f"{self.bold_style}{self.theme[0]}"
        )
        console.print(
            "="*len(self.get_name_space()), style=f"\n{self.bold_style}{self.theme[0]}"
        )

        # Description
        console.print(
            self.get_description(), style=f"{self.bold_style}{self.theme[1]}"
        )
        




    def run(self, function):
        """
        Run whatever the developer wants to run
        `function`:function to be run
        """
        function()

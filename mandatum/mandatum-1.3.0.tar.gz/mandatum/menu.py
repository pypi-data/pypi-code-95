# Importings
from rich.console import Console
import sys

# Initial Setup
console = Console()


# Menu Class
class Menu():
    """Menu class"""
    def __init__(self, options=[], theme=["red", "green", "blue"], bold_text=False):
        """
        Creates menu for the application, Parameters are set by default.

        Parameters:
    
        `options` : Options to be displayed in the menu
        `theme` : Theme for the menu
        `bold_text` : Asks if bold text is required
        """
        
        # Theme for menu
        self.theme = theme

        # Options on menu
        self.options = options

        # Bold Text
        self.bold_text = bold_text
        self.bold_style = ""

        # If bold text is required
        if self.bold_text == True:
            self.bold_style = "bold "

        # If not
        else:
            self.bold_style = ""

        # Spacing
        self.spacing = 4



    def get_theme(self):
        """Returns the current theme"""
        return self.theme



    def change_theme(self, theme=["red", "green", "blue"]):
        """
        Changes the theme of the menu
        
        Parameter:
        `theme` : New theme of the menu
        """
        self.theme = theme




    def get_options(self):
        """Return all the options"""
        return self.options
    




    def change_options(self, options=[]):
        """
        To change all the options of the menu, It deletes all the options and then add new ones.
        
        `options`:New options for the menu 
        """
        self.options = options




    def add_option(self, new_option=""):
        """
        To add new option at the last of the menu

        `new_option`:New option to be added
        """
        self.options.append(new_option)
    



    def delete_option(self, option=""):
        """
        Deletes a option

        `option`:Option to be deleted
        """
        try:
            self.options.remove(option)
            return True
        # Handling error
        except:
            console.print(
                f"\nMake sure you have {option} in your menu\n", style="bold red"
            )
            sys.exit()





    def config_space(self, space=4):
        # configures space on both sides of mode name
        self.spacing = space





    def change_bold_text(self, bold_text=False):
        # Changing bold text
        self.bold_text = bold_text




    def get_menu(self):
        # Return mode name with space on both sides
        _space = " "
        # Looking For errors
        try:
            return f"{_space*self.spacing}Menu{_space*self.spacing}"
        # Asking developer to fix errors
        except:
            console.print(
                "\nMake sure you have added a valid number for text spacing.\n", style="bold red"
            )
            sys.exit()





    def start(self):
        """
        Prints the menu on the screen
        """

        menu_text = self.get_menu()

        # Displaying Menu
        console.print(
            menu_text, style=f"{self.bold_style}{self.theme[0]}"
        )
        console.print(
            "="*len(menu_text), style=f"{self.bold_style}{self.theme[0]}"
        )

        # Displaying options
        for i in range(0, len(self.options)):
            # Displaying option no.
            option_no = f"[{self.bold_style}{self.theme[1]}]{str(i+1)}"
            console.print(
                option_no, style=f"{self.bold_style}{self.theme[1]}", end="."
            )

            # Displaying option
            option = self.options[i]
            console.print(
                option, style=f"{self.bold_style}{self.theme[2]}"
            )
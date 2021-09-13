# Importings
from rich.console import Console


# Initial setup
console = Console()



# Alerts
class Alert():
    """Alert Class"""
    def __init__(self, color="red", bold_text=False):
        """
        Used for alerting the users

        Parameters:
        `color`:Color for the alert
        `bold_text`:Asks if bold text is required
        """
        
        # Color for alerts
        self.color = color

        # bold text
        self.bold_text = bold_text
        self.bold_style = ""

        # If bold text is required
        if self.bold_text == True:
            self.bold_style = "bold "

        # if not
        else:
            self.bold_style = ""
    





    def alert(self, message=""):
        """
        alerts the user with a message
        `message`:Message to alert
        """
        # Prints alert message
        console.print(
            message, style=f"{self.bold_style}{self.color}"
        )

    
    
    
    
    def change_bold_text(self, bold_text=False):
        """Changing bold text"""
        self.bold_text = bold_text

    
    
    
    
    def change_color(self, color="red"):
        """Changing color"""
        self.color = color
        return True













# Warnings
class Warning():
    """Warning class"""
    def __init__(self):
        """Init Function for the class"""

        # Bold Text
        self.bold_text = False
        self.bold_style = ""
    



    def check_bold_text(self, bold_text):
        # If bold text is required
        if bold_text == True:
            self.bold_style = "bold "
            
            return True

        # If not
        else:
            self.bold_style = ""

            return False





    # Main warn function
    def warn(self, message="", color="red", bold_text=False):
        """
        Warns user by priniting message on the display

        Parameters:
        `message`:Message to be displayed
        `color`:Color for the warning
        `bold_text`:Asks if bold text is required
        """
        
        # Color for warning message
        self.color = color

        # Checking bold text
        self.bold_text = bold_text
        self.check_bold_text(bold_text=self.bold_text)

        # Printing warning message
        console.print(
            message, style=f"{self.bold_style}{self.color}"
        )
    






    def change_bold_text(self, bold_text=False):
        """Changing bold text"""
        self.bold_text = bold_text


class Console_Color:
    colors = {
                "text": "\033[0m",
                "log": "\033[96m",
                "info": "\033[94m",
                "secondary": "\033[95m",
                "warning": "\033[93m",
                "error": "\033[91m",
                "BOLD": "\033[1m",
                "UNDERLINE": "\033[4m"
            }

    def __init__(self, color = "text"):
        self.color = self.colors[color]
class Cmd:
    """
    Subclass this class and pass it to `register_commands`.
    """
    def get_name(self, func):
        """
        Override this function to get the names of the class functions.
        """
        return func.__name__

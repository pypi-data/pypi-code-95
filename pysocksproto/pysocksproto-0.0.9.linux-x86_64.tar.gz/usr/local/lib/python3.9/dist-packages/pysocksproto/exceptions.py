class UnsuccessfulRepcode(Exception):
        def __init__(self, repcode:int, *args: object) -> None:
            super().__init__(*args)
            self.repcode = repcode
            
        def __str__(self) -> str:
            return f"Unsucessful repcode {self.repcode}"

class AuthException(Exception):

    def __str__(self) -> str:
        return "Invalid Authenfication"
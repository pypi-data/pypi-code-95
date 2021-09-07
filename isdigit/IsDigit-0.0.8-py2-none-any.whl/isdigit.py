import ast, typing

try:
    from discord.ext import commands
except ImportError:
    commands = None

class IsDigit:
    def __init__(self, *, allow_floats: bool = False, allow_ints: bool = True) -> None:
        """Class constructor

        :param allow_floats: Whether or not a float should return True, defaults to False
        :type allow_floats: bool, optional
        :param allow_ints: Wether or not an int should return True, defaults to True
        :type allow_ints: bool, optional
        """
        self.allow_floats = allow_floats
        self.allow_ints = allow_ints

    def is_digit(self, item: str, return_digit: bool = False) -> typing.Union[bool, int, float]:
        """Checks if a string is a digit

        :param item: The string to check
        :type item: str
        :param return_digit: Should the function return the float/int version of the string?, defaults to False
        :type return_digit: bool, optional
        :return: The float/int version of the string, or the bool if return_digit is False
        :rtype: typing.Union[bool, int, float]
        """
        item_type = None
        try:
            if return_digit:
                digit_to_return = int(item)
            else:
                int(item)
            # type of 1 is int, so isinstance will work correctly
            item_type = 1
        except ValueError:
            try:
                if return_digit:
                    digit_to_return = float(item)
                else:
                    float(item)
                # type of 0.1 is float, so isinstance will work correctly
                item_type = 0.1
            except ValueError:
                return False
        if isinstance(item_type, int):
            if return_digit:
                return digit_to_return
            return self.allow_ints
        elif isinstance(item_type, float):
            if return_digit:
                return digit_to_return
            return self.allow_floats
        else:
            return False

    def __call__(self, item: str) -> bool:
        return self.is_digit(item)

    def __repr__(self) -> str:
        return f"IsDigit(allow_floats={self.allow_floats}, allow_ints={self.allow_ints})"

    async def convert(self, ctx, argument) -> typing.Optional[int]:
        if not commands:
            raise Exception(f"discord.ext is not installed, please install it to use this converter")
        if (item := self.is_digit(argument, return_digit=True)):
            return item
        else:
            raise commands.BadArgument(f'{argument} is not a valid number.')
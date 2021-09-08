from difflib import get_close_matches
from sys import exit as sys_exit
from sys import stdout

from blessed import Terminal


class Selection:
    """ Selection object passed as the output of Selection Prompt.
        Contains additional information.

    :attr value (STR): User selection.
    :attr index (INT): Index of given input list.
    :attr search (STR): Search query of user.
    :attr search_result (LIST): Provided search result.

    The index cannot be determined when the user requested a search and
    the selected item is more than once inside the given selection.
    This is due to difflib.get_close_matches not returning the index of the result.

    """

    def __init__(self, value, search=None, search_result=None, index=None):

        self.value = value
        self.index = index
        self.search = search if search else None
        self.search_result = search_result if search else None

    def __str__(self):

        return self.value

    def __repr__(self):

        return f"<Selection '{self.value}'>"


class SelectionPrompt:

    def __init__(self, selection, info="", prompt="> ", search="", current=0, rows=4, cutoff=0.15, amount_results=100, highlight_color="yellow", full_exit=True, ignore_warnings=False):
        """ Prompt for user selection.

        Arguments
        ---------
        :arg selection (LIST): The available choices to display the user.


        Keyword Arguments
        -----------------
        :arg info (STR): Information shown above prompt. / Prompt title.
        :arg prompt (STR): Text in front of user input.
        :arg search (STR): Pre-insert text into the input prompt.
        :arg current (INT): Current item of list as default selection.
        :arg rows (INT): Amount of visible choices.
        :arg cutoff (FLOAT): Search precision.
        :arg amount_results (INT): The max amount of search results to show.
        :arg highlight_color (STR): Search highlight color.
        :arg full_exit (BOOL): Exit completely or pass None on KeyBoardInterrupt or ESC.
        :arg ignore_warnings (BOOL): Ignore warnings shown by this class.

        TODO:
        - Rename the variables for better understanding.

        """

        # Variables | Static variables
        self._term = Terminal()

        self._key_timeout = 5

        self._highlight_color = {"black": self._term.black, "red": self._term.red, "green": self._term.green, "yellow": self._term.yellow, "blue": self._term.blue, "magenta": self._term.magenta, "cyan": self._term.cyan, "white": self._term.white}[highlight_color]  # TODO: Find a better solution

        self._default_cursor_pos = {"x": len(prompt),
                                    "y": info.count("\n") + 1 if info else 0}

        # Variables | Static User Variables
        self._selection = [str(option) for option in selection]
        self._info = info
        self._prompt = prompt
        self._rows = rows
        self._cutoff = cutoff
        self._amount_results = amount_results
        self._full_exit = full_exit
        self._ignore_warning = False

        # Variables | Dynamic variables (Terminal State)
        self._cursor_pos = None
        self._written_lines = 0

        # Variables | Dynamic variables (List)
        self._reset_current_selection(self._selection, current=current)
        self._return_placeholder = None

        # Variables | Dynamic variables (Input)
        self._search = search
        self._searching = False  # TODO: Find a better solution to determine the end of the search.

        if self._rows >= self._term.height and not self._ignore_warning:

            print(self._term.yellow("Warning: Please increase terminal size or reduce rows."))

    def show(self):
        """ Entry Point | Main Loop
        """

        with self._term.cbreak():

            while True:

                self._render()

                # KEY BINDINGS
                key = self._term.inkey(timeout=self._key_timeout)

                self._key_bindings(key)

                self._flush()

                # Return value if set
                if self._return_placeholder is not None:

                    return self._return_placeholder

    def _exit(self):
        """ On KeyBoardInterrupt or ESC.
        """

        self._flush()

        if self._full_exit:

            sys_exit()

    def _print(self, out):
        """ Internal way of displaying content while counting all the written lines.

        The reason for counting all the written lines is so that we can predict the cursor position.
        """

        stdout.write(out + "\n")
        stdout.flush()

        self._written_lines += 1 + out.count("\n")

    def _flush(self):
        """ Clear the screen from the cursor position downwards.

        An alternative would be overwriting, though it does not clear the remaining characters.
        - self._reset_cursor instead of self._flush
        """

        self._reset_cursor()

        stdout.write(self._term.clear_eos)
        stdout.flush()

    def _key_bindings(self, key):
        """ Function for all the key bindings.
        """

        if key.name == "KEY_ESCAPE":

            self._exit()

        elif key.name == "KEY_ENTER" and \
                len(self._current_selection) != 0:

            self._return_selection()

        elif key.name == "KEY_DOWN":

            self._navigate_menu(1)

        elif key.name == "KEY_UP":

            self._navigate_menu(-1)

        elif key.name == "KEY_BACKSPACE" and \
                self._search != "":  # On Backspace

            self._search = self._search[:-1]

        elif len(key) == 1 and key.name is None and \
                len(self._search) < (self._term.width - len(self._prompt)):  # On Key except for special keys

            self._search += key

    def _move_cursor(self, cursor_x, cursor_y):
        """ Move the cursor to a different position, by calculating delta.

        The x position should be 0 after the first stdout writes.
        Therefore we can assume x to be 0 and set y to the number of written lines.
        """

        # Reset position variable (Important for calculating delta) if x pos not known
        if self._cursor_pos is None:

            self._cursor_pos = {"x": 0, "y": self._written_lines}

        # Calculate and move delta position
        full_write = ""

        if self._cursor_pos["y"] < cursor_y:
            full_write += self._term.move_down * (cursor_y - self._cursor_pos["y"])

        elif self._cursor_pos["y"] > cursor_x:
            full_write += self._term.move_up * (self._cursor_pos["y"] - cursor_y)

        if self._cursor_pos["x"] < cursor_x:
            full_write += self._term.move_right * (cursor_x - self._cursor_pos["x"])

        elif self._cursor_pos["x"] > cursor_x:
            full_write += self._term.move_left * (self._cursor_pos["x"] - cursor_x)

        stdout.write(full_write)
        stdout.flush()

        self._cursor_pos = {"x": cursor_x, "y": cursor_y}

    def _reset_cursor(self):
        """ Reset the cursor position to 0, 0 without flushing the screen and reset the written_lines counter.
        """

        self._move_cursor(0, 0)

        self._written_lines = 0
        self._cursor_pos = None

    def _render(self):
        """ Render the interface to the terminal.
        """

        # Display the info
        if self._info:
            self._print(self._info)

        # Display the input prompt
        self._print(self._prompt + self._search)

        # Display the selection
        self._refresh_currently_shown()

        for pos, option in enumerate(self._currently_shown):

            option_msg = self._term.reverse(option) if pos + self._current_position[0] == self._current else option

            self._print(option_msg)

        # Move the cursor to the input prompt.
        self._reset_cursor()  # TODO: (Strange Issue) Cursor position changes, needs further investigation.
        self._move_cursor(self._default_cursor_pos["x"] + len(self._search), self._default_cursor_pos["y"])

    def _reset_current_selection(self, selection, current=0):
        """ Switch to another selection.
        """

        self._current_selection = selection
        self._current = current
        self._current_position = [self._current, (self._rows + self._current)]

        # self._currently_shown = self._current_selection[self._current:(self._rows + self._current)]

    def _refresh_currently_shown(self):
        """ Update the visible segment of the list.
        """

        if self._search != "":  # TODO: On search wierd flashing: Probably because get_close_match needs time to calculate

            self.best_matches = get_close_matches(self._search, self._selection, cutoff=self._cutoff, n=self._amount_results)

            best_matches_hl = [match.replace(self._search, self._highlight_color(self._search)) for match in self.best_matches]

            if not self._searching:

                self._reset_current_selection(best_matches_hl)

                self._searching = True

            else:

                self._current_selection = best_matches_hl

        elif self._searching:

            self._reset_current_selection(self._selection)

            self._searching = False

        self._currently_shown = self._current_selection[self._current_position[0]:self._current_position[1]]

    def _navigate_menu(self, up_or_down):
        """ Navigates the Menu one item down or up

        :arg up_or_down (INT): -1 for up and 1 for down.

        """

        # Check for list border
        if self._current == 0 and up_or_down < 0 or \
           self._current == len(self._current_selection) - 1 and up_or_down > 0:

            return

        # Change current
        if up_or_down < 0:

            self._current -= 1

        elif up_or_down > 0:

            self._current += 1

        # Change menu viewpoint
        if self._current == self._current_position[0] - 1 and \
           up_or_down < 0:

            self._move_list_view(-1)

        elif self._current == self._current_position[1] and \
                up_or_down > 0:

            self._move_list_view(1)

    def _move_list_view(self, up_or_down):
        """ Navigates the list segment one up or down.

        :arg up_or_down (INT): -1 for up and 1 for down.

        """

        self._current_position[0] += up_or_down
        self._current_position[1] += up_or_down

    def _return_selection(self):
        """ Return the user selection whilst also providing additional info.
        """

        self._flush()

        # Decolorize search output
        return_value_nhl = self._current_selection[self._current].replace(self._highlight_color(self._search), self._search)

        # Get index (TODO: Find alternative)
        if self._search != "":

            if self._selection.count(return_value_nhl) != 1:

                if not self._ignore_warning:

                    print(self._term.yellow("Warning: Cannot determine the exact index of search result."))

            index = self._selection.index(return_value_nhl)

        else:

            index = self._current

        # Create Object
        return_value = Selection(return_value_nhl, search=self._search, search_result=self._current_selection, index=index)

        self._return_placeholder = return_value


def select(selection, **kwargs):
    """ Function for additional tasks to increase user-friendliness.
        Executes the SelectionPrompt.
    """

    prompt = SelectionPrompt(selection, **kwargs)

    try:

        user_selection = prompt.show()

    except KeyboardInterrupt:

        prompt._exit()

    return user_selection

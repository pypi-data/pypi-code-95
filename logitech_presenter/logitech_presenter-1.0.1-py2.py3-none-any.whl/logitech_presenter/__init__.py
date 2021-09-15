"""Listens to the Logitech Presenter and fires callbacks appropriately."""

__version__ = "1.0.1"


import pynput.keyboard
import time


def generate_on_press(on_next, on_prev, on_slideshow, on_black_screen):
    """Generate a key press callback that calls the appropriate sub-callback"""

    def on_press(key):
        try:
            if key in [pynput.keyboard.Key.esc, pynput.keyboard.Key.f5]:
                if on_slideshow:
                    on_slideshow()
            elif key == pynput.keyboard.Key.page_up:
                if on_prev:
                    on_prev()
            elif key == pynput.keyboard.Key.page_down:
                if on_next:
                    on_next()
            elif key.char == ".":
                if on_black_screen:
                    on_black_screen()
        except AttributeError:
            # some other special key was pressed, but we don't care about it
            pass

    return on_press


def setup_listeners(
    on_next=None,
    on_prev=None,
    on_slideshow=None,
    on_black_screen=None,
    block=False
):
    """Start listening for Logitech Presenter button presses

    Args:
        on_next (function, optional): Called with no arguments when the
            Next button or the PageDown key is pressed. Defaults to None.
        on_prev (function, optional): Called with no arguments when the
            Previous button or the PageUp key is pressed. Defaults to None.
        on_slideshow (function, optional): Called with no arguments when
            the Slide Show button or the Esc/F5 keys are pressed.
            Defaults to None.
        on_black_screen (function, optional): Called with no arguments when
            the Black Screen button or the period (".") key is pressed.
            Defaults to None.
        block(bool, optional): Whether or not this function should block until
            interrupted. Defaults to False.
    """
    listener = pynput.keyboard.Listener(
        generate_on_press(
            on_next=on_next,
            on_prev=on_prev,
            on_slideshow=on_slideshow,
            on_black_screen=on_black_screen,
        )
    )
    listener.start()  # start to listen on a separate thread
    if block:
        listener.join()  # remove if main thread is polling self.keys


if __name__ == "__main__":
    print("Listening and printing Logitech Presenter button events.")
    setup_listeners(
        on_next=lambda: print("next"),
        on_prev=lambda: print("previous"),
        on_slideshow=lambda: print("slideshow toggle"),
        on_black_screen=lambda: print("black screen toggle"),
        block=False
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"Exiting")

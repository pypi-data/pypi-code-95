from pyautogui import press, write
import time

def wait_write_press(delay: int, text: str, hotkey: str):
    '''
    This function is to perform /wait, write, press/ sequence

    Args:
        delay: (int) - delay time in [seconds]
        text: (str) - text to be written
        hotkey: (str) - hotkey to be pressed
    '''
    time.sleep(delay)
    write(text)
    press(hotkey)


def wait_press(delay: int, hotkey: str):
    '''
    This function is to perform /wait, press/ sequence

    Args:
        delay: (int) - delay time in [seconds]
        hotkey: (str) - hotkey to be pressed
    '''
    time.sleep(delay)
    press(hotkey)


def wait_write(delay: int,text: str):
    '''
    This function is to perform /wait, write/ sequence

    Args:
        delay: (int) - delay time in [seconds]
        text: (str) - text to be written
    '''
    time.sleep(delay)
    write(text)
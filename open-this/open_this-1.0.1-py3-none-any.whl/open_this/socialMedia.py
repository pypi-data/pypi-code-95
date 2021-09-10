# import statement
import pyperclip, sys, webbrowser

# check whether the Command Line has more argument
# If it has args then with the help of sys module extract -
# each args and join them as the string and store that in address variable
# Else get the address from clipboard with pyperclip.paste() method

def main():
    if len(sys.argv) > 1:
        social_media = ''.join(sys.argv[1:])
    else:
        social_media = pyperclip.paste()
    
    webbrowser.open(f'https://{social_media}.com')

if __name__ == '__main__':
    main()
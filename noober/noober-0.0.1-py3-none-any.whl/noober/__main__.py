def Prompt(message, strict="yes", input_type="str", **kwargs):
    if strict == "yes":
        while True:
            prompt_input = input(message)
            if input_type == "str":
                try:
                    prompt_return = str(prompt_input)
                    break
                except:
                    print("Given Input is not a string / text Try again")
            if input_type == "int":
                try:
                    prompt_return = int(prompt_input)
                    break
                except:
                    print("Given Input is not a integer Try again")
            if input_type == "float":
                try:
                    prompt_return = float(prompt_input)
                    break
                except:
                    print("Given Input is not an float / decimal Try again")
        return prompt_return
    if strict == "no":
        prompt_input = input(message)
        if input_type == "str":
            try:
                prompt_return = str(prompt_input)
            except:
                print("Given Input is not a string / text Try again")
        if input_type == "int":
            try:
                prompt_return = int(prompt_input)
            except:
                print("Given Input is not a integer Try again")
        if input_type == "float":
            try:
                prompt_return = float(prompt_input)
            except:
                print("Given Input is not an float / decimal Try again")
        return prompt_return

def YesNo(message, strict="yes"):
    if strict == "yes":
        while True:
            yes_no_input = str.lower(input(message + " Y/N : "))
            if yes_no_input == "y" or "yes":
                yes_no = True
                break
            if yes_no_input == "n" or "no":
                yes_no = False
                break
        return yes_no
    if strict == "no":
        yes_no_input = str.lower(input(message + "Y/N : "))
        if yes_no_input == "y" or "yes":
            yes_no = True
        if yes_no_input == "n" or "no":
            yes_no = False
        return yes_no

def Shorten(url, copy="no"):
    import requests
    import pyperclip
    page = requests.get(f'https://tinyurl.com/api-create.php?url={url}')
    short_url = str(page.content).replace("b'", "").rstrip("'")
    if copy == "no":
        pass
    if copy == "yes":
        pyperclip.copy(short_url)
    return short_url

def Time_now():
    from time import strftime
    from datetime import datetime
    current_time = datetime.now().strftime("%H:%M:%S")
    return current_time

def Time_date_now():
    from datetime import date
    current_time = Time_now()
    current_date = str(date.today())
    return f'{current_time}  {current_date}'

def Option(message, options, strict="yes"):
    if strict == "yes":
        while True:
            option_chose = input(f'{message} from {options} : ')
            if option_chose in options:
                option_to_return = option_chose
                break
            print("Option Choose Not in Acceptable List")
        return option_to_return
    if strict == "no":
        option_chose = input(f'{message} from {options} : ')
        if option_chose in options:
            return option_chose
        else:
            return "Option Choose Not in Accepatble List, Try again"

def Win_notify(title, message, duration=15, threaded=True, icon=None):
    from win10toast import ToastNotifier
    notifier = ToastNotifier()
    notifier.show_toast(title, message, duration=duration, threaded=threaded, icon_path=icon)

def Splash(title, content, icon="no", duration=15, function_after="no", font=("Cascadia Code", 72), fg="black", bg="#F0F0F0"):
    import tkinter as tk
    from tkinter import Label, mainloop
    splash_gui = tk.Tk()
    size = f'{splash_gui.winfo_screenwidth()}x{splash_gui.winfo_screenheight()}'
    splash_gui.geometry(size)
    splash_gui.title(title)
    splash_gui.overrideredirect(True)

    label = Label(splash_gui, text=content, fg=fg, bg=bg, font=font)
    label.pack(pady= int(splash_gui.winfo_screenheight()) / 4)

    if function_after == "no":
        def destroy_gui():
            splash_gui.destroy()
        duration = duration * 1000
        splash_gui.after(duration, destroy_gui)
    else:
        duration = duration * 1000
        splash_gui.after(duration, function_after)

    mainloop()
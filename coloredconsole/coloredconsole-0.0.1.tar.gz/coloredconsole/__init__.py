version = "0.0.1"

import random;

def color(string, color):
  if type(string) is not str:
    string_type = type(string);
    print(f"\u001b[31mError: expected type \"str\", got \"{string_type}\".") 
  else:
    selected_color = None;
    color = color.lower();

    if color == "red":
      selected_color = "\u001b[31m";
    elif color == "green" or color == "lime":
      selected_color = "\u001b[32m"
    elif color == "blue":
      selected_color = "\u001b[34m";
    elif color == "magenta" or color == "purple":
      selected_color = "\u001b[35m";
    elif color == "cyan":
      selected_color = "\u001b[36m";
    elif color == "yellow":
      selected_color = "\u001b[33m";
    elif color == "white" or color == "wht":
      selected_color = "\u001b[37m";
    elif color == "black" or color == "blk":
      selected_color = "\u001b[30m";
    elif color == "random":
      color_list = ["\u001b[30m", "\u001b[37m", "\u001b[33m", "\u001b[36m", "\u001b[35m", "\u001b[34m", "\u001b[31m", "\u001b[32m"];
      rng = random.randint(0, len(color_list) - 1);

      selected_color = color_list[rng];
    else:
      return print(f"\u001b[31mError: invalid color type.")
    return f"{selected_color}{string}";

def cprint(string, color):
  if type(string) is not str:
    string_type = type(string);
    print(f"\u001b[31mError: expected type \"str\", got \"{string_type}\".") 
  else:
    selected_color = None;
    color = color.lower();

    if color == "red":
      selected_color = "\u001b[31m";
    elif color == "blue":
      selected_color = "\u001b[34m";
    elif color == "magenta" or color == "purple":
      selected_color = "\u001b[35m";
    elif color == "cyan":
      selected_color = "\u001b[36m";
    elif color == "yellow":
      selected_color = "\u001b[33m";
    elif color == "white" or color == "wht":
      selected_color = "\u001b[37m";
    elif color == "black" or color == "blk":
      selected_color = "\u001b[30m";
    else:
      return print(f"\u001b[31mError: invalid color type.")
    return print(f"{selected_color}{string}");

cprint("Test", "red")

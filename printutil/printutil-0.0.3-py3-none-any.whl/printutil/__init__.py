# PrintUtil By Rambovic45

# Print
class colors:
    WHITE = '\033[0m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    VIOLET = '\033[95m'
class styles:
    BOLD = '\033[1m'
    RESET = '\033[0m'

def error(msg):
    print(colors.RED + f"[ERROR] {msg}" + styles.RESET)
def succes(msg):
    print(colors.GREEN + f"[SUCCES] {msg}" + styles.RESET)
def warn(msg):
    print(colors.YELLOW + f"[WARN] {msg}" + styles.RESET)
def log(msg):
    print(f"[LOG] {msg}" + styles.RESET)
def custom(color, prefix, text):
    print(color + f"[{prefix}] {text}" + styles.RESET)
def ResetPrint(msg):
    print(msg + styles.RESET)
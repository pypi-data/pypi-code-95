import sys


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}

path = sys.path[4]+'\\data.txt'

def cookie():
    with open(path) as f:
        msg = f.read()
    return {'SESSDATA':msg}
from charting import *
from tokens import *
from time import sleep

# can call any function from the above here for testing but all you do is import the folder for pypi functionality
counter = 0
#sleep(60)
while True:
    counter +=1
    print(get_token_price("Cardano",'usd'))
    print(counter)
    sleep(30)

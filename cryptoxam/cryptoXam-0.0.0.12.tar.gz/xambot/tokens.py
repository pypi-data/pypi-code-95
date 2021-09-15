from pycoingecko import CoinGeckoAPI
import pandas as pd
from charting import *
import __init__
cg = CoinGeckoAPI()

def get_tokens():
    # API command to get list of all tokens and convert to dataframe and to a csv updated
    tokens = cg.get_coins_list()
    data = pd.DataFrame.from_dict(tokens)
    data.to_csv('coins.csv')
    print(data)
    return data


# token must be full project typed name, Ethereum not ETH
# vs currency is what you want to compare it to
def get_token_price(token,vs_currency):
    return cg.get_price(token,vs_currency)

#show all the currencies you can check against !!
def show_vs_currencies():
    print(cg.get_supported_vs_currencies())


#shows the top 100 coins and alot of market information compared the currency stated in the function
# could also use a function to filter this down
def show_market(currency):
    info = pd.DataFrame.from_dict(cg.get_coins_markets(currency))
    #print(info)
    return info

#return financial information based on a coin
# can pass a list into either parameters here
def coin_info(name,market):
    data = cg.get_price(ids=name, vs_currencies=market, include_market_cap='true', include_24hr_vol='true', include_24hr_change='true', include_last_updated_at='true')
    return data



# use this data to find all coins within 24hr that have a 24hr % change of different brackets
#type means whether we want to see losing or winning coins
def tfh_change(market,change):

    change = change.lower()
    data = show_market(market)

    data = data[['id','symbol','current_price','price_change_24h','low_24h','high_24h']]
    
    data['24_change_percent'] = data['price_change_24h'] / data['current_price'] * 100

  
    if change[0] =='w':
        data = data[data['24_change_percent'] >= 10]
    elif change[0] =='l':
        data = data[data['24_change_percent'] <= 0]
    else:
        print('\n\n\n')
        print('!!! VALUE ERROR !!!: Change value must be either winner or loser, showing 24 hour change % over 10% or under 0% respectively')

    

tfh_change('usd','linner')

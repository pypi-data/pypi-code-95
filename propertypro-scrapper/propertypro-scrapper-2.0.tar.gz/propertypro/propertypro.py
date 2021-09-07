from numpy import NaN
import pandas as pd
import requests
import math
import re

from bs4 import BeautifulSoup


class Propertypro:
    """
    web-scraper tool for scraping data on propertypro.ng
    
    Parameters:
        num_samples (int): The number of samples of data to be scraped. 
        location (list): list of keywords to scrape

    Returns:
        pd.DataFrame: Returns a dataframe with the following categories as columns:
        title, location, price, number of bedrooms, toilets, bathroom, whether it is furnished, serviced and newly built
        
    """

    def __init__(self) -> None:
        self.no_samples = 0


    def process_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        cleans data from the provided Dataframe.
        :param data: Scraped data .
        :return: pandas dataframe
        """
        data = dataframe
        data = data.dropna()
        data['rooms'] = data['rooms'].str.split('\n')
        data[['nothing', 'bedroom', 'bathroom', 'toilet', 'remove']] = pd.DataFrame(data['rooms'].tolist(), index= data.index)
        data['bedroom'] = data['bedroom'].str.strip('beds')
        data['bathroom'] = data['bathroom'].str.strip('baths')
        data['toilet'] = data['toilet'].str.strip('Toilets')
        # data['price'] = data['price'].str.replace(',', '')
        data['price'] = data['price'].str.replace(r'[^0-9]+','')
        data['furnishing'] = data['furnishing'].str.split('\n')
        data['newly_built'] = data['furnishing'].apply(lambda x: ''.join(['1' if "Newly Built" in x else '0']))
        data['furnished'] = data['furnishing'].apply(lambda x: ''.join(['1' if "Furnished" in x else '0']))
        data['serviced'] = data['furnishing'].apply(lambda x: ''.join(['1' if "Serviced" in x else '0']))
        data = data.drop(columns=['rooms', 'nothing', 'remove', 'furnishing'])
        return data


    def scrape_data(self, no_samples, keywords):
        """
        Scrapes data from provided urls
        :param : no_samples, keywords
        :return: pandas dataFrame.
        """

        data = {"title": [], "location": [], "furnishing": [], "rooms": [], "price": []}
        for keyword in keywords:
            page_url = []
            for i in range(0,round((no_samples/22))):
                page_url.append('https://www.propertypro.ng/property-for-rent/in/' + keyword + '?search=&type=&bedroom=&min_price=&max_price=&page=' + str(i))
            for links in page_url:
                response = requests.get(links)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for title in soup.find_all('h2', { 'class':"listings-property-title" }):
                    data["title"].append(title.text)
                    data["location"].append(keyword)
                for furnishing in soup.find_all('div', {'class': "furnished-btn"}):
                    data["furnishing"].append(furnishing.text)
                for rooms in soup.find_all('div', {'class': "fur-areea"}):
                    data["rooms"].append(rooms.text)
                for price in soup.find_all('h3', { 'class': 'listings-price' }):
                    data["price"].append(price.text)
            page_url.clear()

        # df = pd.DataFrame(data)
        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.transpose()
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        df = self.process_data(df)
        return df

    # def clean_dataframe(self) -> pd.DataFrame:
    #     """
    #     Function which combines all functions required for cleaning scraped data.
        
    #     :param : None
    #     :return: pandas dataFrame.
    #     """

    #     data = self.process_data(self.collect_information())
    #     if self.export_to_csv:
    #         self.export_to_csv(data)
    #     return data

    # def export_to_csv(self, data: pd.DataFrame) -> None:
    #     """
    #     Exports a dataframe to a .csv file in working dir.
    #     :param data: pandas dataframe
    #     :return: None
    #     """
    #     now = datetime.now()
    #     timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    #     return data.to_csv(f"{self.category}_{timestamp}.csv", index=False)


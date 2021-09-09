from bs4 import BeautifulSoup
import requests as r
import pandas as pd


class TypeRacerScraper:
    def __init__(self, userID, numberOfResults):
        self.userID = userID
        self.numberOfResults = numberOfResults
        self.url = "https://data.typeracer.com/pit/race_history?user=" + self.userID + "&n=" + self.numberOfResults
        self.source = r.get(self.url)
        self.parsedSource = BeautifulSoup(self.source.content, "html.parser")


    def result_json(self):
        race     = []
        speed    = []
        accuracy = []
        points   = []
        place    = []
        values = self.parsedSource.find("table", class_="scoresTable").find_all("tr")

        for value in values:
            try:
                items = value.find_all("td")

                race.append(items[0].string.strip())
                speed.append(items[1].string.strip())
                accuracy.append(items[2].string.strip())
                points.append(items[3].string.strip())
                place.append(items[4].string.strip())
            except:
                pass

        d = {"Race": race, "Speed": speed, 
             "Accuracy":accuracy, "Points": points
             ,"Place": place}

        df = pd.DataFrame(data=d).reset_index()
        return df.to_json(orient="split")



from requests import get
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Dict, List, Tuple
try:
    from anime_reference.constants import *
    from anime_reference.utils import clean_str_list, format_episode_links, clean_text
except:
    from constants import *
    from utils import clean_str_list, format_episode_links, clean_text

class Naruto:
    """
    A class to represent a Naruto anime title.
    ...

    Attributes
    ----------
    title : str
        title of the anime

    Methods
    -------
    _check_title():
        Checks if the title is valid.

    _check_episode_name(episode_name):
        Checks if the episode name is valid

    _get_link():
        Gets the link of episodes associated with the anime title

    _episode_link_dict():
        Gets the episode:link dictionary

    get_episodes():
        Gets a dataframe of episode #, title, and airdate (Japanese and English)

    summary(episode_name):
        Gets the summary of the given episode name

    episode_names():
        Gets a list of episode names

    movie_names():
        Gets a list of movie names
    """
    def __init__(self, title: str) -> None:
        self.title = title
        self._check_title()
        return None

    def _check_title(self) -> None:
        if self.title not in NARUTO.keys():
            print(f"Anime \"{title}\" is not a valid anime title.")
            # TODO: Add a helper function that asks "Did you mean (title)?"
            return None
        
    def _check_episode_name(self, episode_name: str) -> None:
        if episode_name not in self.episode_names:
            print(f"Episode \"{episode_name}\" is not a valid {self.title} episode name.")
            # TODO: Add a helper function that asks "Did you mean (episode name)?"
            return None
        
    def _check_movie_name(self, movie_name: str) -> None:
        if movie_name not in self.movie_names:
            print(f"Movie \"{movie_name}\" is not a valid {self.title} movie name.")
            # TODO: Add a helper function that asks "Did you mean (movie name)?"
            return None
        
    def _get_link(self) -> str:
        return NARUTO[self.title] # link for the all epsiodes, movies of the different naruto titles

    @property
    def _episode_link_dict(self) -> Optional[Dict[str, str]]:
        link = self._get_link()
        response = get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = list(map(str, soup.find_all('table')))
            if self.title == "naruto":
                links = tables[0] # Table 1 is for Naruto (original) episodes
                links = BeautifulSoup(links, 'html.parser').find_all('a')
                links = list(map(str, links))
                episode_names = clean_str_list(links, search_str='title="(.*)"')
                links = format_episode_links("https://naruto.fandom.com", links)
                return dict(zip(episode_names, links))
            elif self.title == "naruto shippuden":
                links = tables[1] # Table 2 is for Naruto Shippuden episodes
                links = BeautifulSoup(links, 'html.parser').find_all('a')
                links = list(map(str, links))
                episode_names = clean_str_list(links, search_str='title="(.*)"')
                links = format_episode_links("https://naruto.fandom.com", links)
                return dict(zip(episode_names, links))
            elif self.title == "boruto":
                links = tables[2] # Table 3 is for Boruto episodes
                links = BeautifulSoup(links, 'html.parser').find_all('a')
                links = list(map(str, links))
                episode_names = clean_str_list(links, search_str='title="(.*)"')
                links = format_episode_links("https://naruto.fandom.com", links)
                return dict(zip(episode_names, links))
        else:
            print(f"Bad response, status code: {response.status_code}")
            return None

    @property
    def _movie_link_dict(self) -> Optional[Dict[str, str]]:
        link = self._get_link()
        response = get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = list(map(str, soup.find_all('table')))
            if self.title == "naruto":
                links = tables[4] # Table 5 is for Naruto (original) movies 
                links = BeautifulSoup(links, 'html.parser').find_all('a')
                links = list(map(str, links))
                movie_names = clean_str_list(links, search_str='title="(.*)"')
                links = format_episode_links("https://naruto.fandom.com", links)
                return dict(zip(movie_names, links))
            elif self.title == "naruto shippuden":
                links = tables[5] # Table 6 is for Naruto Shippuden movies 
                links = BeautifulSoup(links, 'html.parser').find_all('a')
                links = list(map(str, links))
                movie_names = clean_str_list(links, search_str='title="(.*)"')
                links = format_episode_links("https://naruto.fandom.com", links)
                return dict(zip(movie_names, links))
            elif self.title == "boruto":
                # TODO: No movies for boruto as of yet
                movie_names, links = [], []
                return dict(zip(movie_names, links))
        else:
            print(f"Bad response, status code: {response.status_code}")
            return None

    def _get_episode_link(self, episode_name: str) -> Optional[str]:
        self._check_episode_name(episode_name)
        try:
            return self._episode_link_dict[episode_name]
        except KeyError:
            return None

    def _get_movie_link(self, movie_name: str) -> Optional[str]:
        self._check_movie_name(movie_name)
        try:
            return self._movie_link_dict[movie_name]
        except:
            return None

    @property
    def dataframe(self) -> Optional[Tuple[pd.DataFrame, pd.DataFrame]]:
        link = self._get_link()
        try:
            response = get(link)
        except:
            return None
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')
            if self.title == "naruto":
                df_episodes = pd.read_html(str(tables))[0]
                df_movies = pd.read_html(str(tables))[4]
            elif self.title == "naruto shippuden":
                df_episodes = pd.read_html(str(tables))[1]
                df_movies = pd.read_html(str(tables))[5]
            elif self.title == "boruto":
                df_episodes = pd.read_html(str(tables))[2]
                df_movies = pd.DataFrame(columns=['#', 'Title', 'Japanese Airdate', 'English Airdate'])
            return df_episodes, df_movies
        else:
            print(f"Bad response, status code: {response.status_code}")
            return None
   
    def episode_summary(self, episode_name: str) -> Optional[str]:
        link = self._get_episode_link(episode_name)
        try:
            response = get(link)
        except:
            return None
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            y = list(map(str,soup.find_all('p')))[1:]
            summary = "".join(s for s in y)
            summary = clean_text(summary)
            return summary
        else:
            print(f"Bad response, status code: {response.status_code}")
            return None
        
    def movie_summary(self, movie_name: str) -> Optional[str]:
        link = self._get_movie_link(movie_name)
        try:
            response = get(link)
        except:
            return None
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            summary = ""
            for paragraph in soup.find_all('p'):
                summary += paragraph.get_text()
            return summary
        else:
            print(f"Bad response, status code: {response.status_code}")
            return None
        
    @property
    def episode_names(self) -> List[str]:
        return list(self._episode_link_dict.keys())

    @property
    def movie_names(self) -> List[str]:
        return list(self._movie_link_dict.keys())
    
if __name__ == "__main__":
    x = Naruto("naruto")
    y = Naruto("naruto shippuden")
    z = Naruto("boruto")

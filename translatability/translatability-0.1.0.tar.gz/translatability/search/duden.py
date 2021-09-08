import bs4
import requests
import re

URL_FORM = "http://www.duden.de/rechtschreibung/{word}"
SEARCH_URL_FORM = "http://www.duden.de/suchen/dudenonline/{word}"

rechtschreibung = re.compile(r"/rechtschreibung/.+")


def search(word, exact=True, return_words=True):
    """
    Search for a word 'word' in duden
    """
    try:
        url = SEARCH_URL_FORM.format(word=word)
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        if soup.find("a", href=rechtschreibung):
            section = soup.find("section", class_="vignette")
            noun_validation = section.find("p", class_="vignette__snippet")
            if "Substantiv," in noun_validation.text.split():
                return True

            else:
                return False

        else:
            return False

    except Exception:
        return False

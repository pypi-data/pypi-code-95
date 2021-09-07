import requests
requests.packages.urllib3.disable_warnings()

def search_for_maps(**kwargs):
    """
    A function used to get JSON user data inside the project.
    """
    if not "maxversion" in kwargs.keys(): kwargs["maxversion"] = "999"
    if not "page" in kwargs.keys(): kwargs["page"] = "0"
    if not "trendsystem" in kwargs.keys(): kwargs["trendsystem"] = "1"
    if not "offset" in kwargs.keys(): kwargs["trendsystem"] = "0"

    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/map/public/top/{str(kwargs['gameMode'])}/search?maxversion={str(kwargs['maxversion'])}&result={str(kwargs['result'])}&page={str(kwargs['page'])}&query={str(kwargs['query'])}", verify=False).json()

def find_top_maps(**kwargs):
    """
    A function used to get JSON top map data inside the project.
    """
    if not "maxversion" in kwargs.keys(): kwargs["maxversion"] = "999"
    if not "page" in kwargs.keys(): kwargs["page"] = "0"
    if not "trendsystem" in kwargs.keys(): kwargs["trendsystem"] = "1"
    if not "offset" in kwargs.keys(): kwargs["trendsystem"] = "0"

    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/map/public/top/{str(kwargs['gameMode'])}/{str(kwargs['time'])}?maxversion={str(kwargs['maxversion'])}&result={str(kwargs['result'])}&page={str(kwargs['page'])}&trendsystem={str(kwargs['trendsystem'])}&offset={str(kwargs['offset'])}", verify=False).json()

def list_new_maps(**kwargs):
    """
    A function used to get JSON new map data inside the project.
    """
    if not "maxversion" in kwargs.keys(): kwargs["maxversion"] = "999"
    if not "page" in kwargs.keys(): kwargs["page"] = "0"

    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/map/public/new/{str(kwargs['gameMode'])}?maxversion={str(kwargs['maxversion'])}&result={str(kwargs['result'])}&page={str(kwargs['page'])}", verify=False).json()

def list_maps_by_user(**kwargs):
    """
    A function used to get JSON user map data inside the project.
    """
    if not "result" in kwargs.keys(): kwargs["result"] = 50
    if not "maxversion" in kwargs.keys(): kwargs["maxversion"] = "999"
    if not "page" in kwargs.keys(): kwargs["page"] = "0"

    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/map/public/user/{str(kwargs['userId'])}?maxversion={str(kwargs['maxversion'])}&result={str(kwargs['result'])}&page={str(kwargs['page'])}", verify=False).json()

def list_comments_on_map(**kwargs):
    """
    A function used to get JSON comment data inside the project.
    """
    before = ""
    if "before" in kwargs.keys(): before = f"&before={str(kwargs['before'])}"
    
    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/comment/public/{str(kwargs['mapId'])}?limit={str(kwargs['limit'])}{before}", verify=False).json()

def get_map_details(**kwargs):
    """
    A function used to get JSON map data from it's ID inside the project.
    """
    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/map/public/{str(kwargs['mapId'])}/meta", verify=False).json()

def get_map_thumbnail_url(**kwargs):
    """
    A function used to get thumbnail data inside the project.
    """
    return f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/map/public/{str(kwargs['mapId'])}/thumb"

def search_for_users(**kwargs):
    """
    A function used to get JSON user data inside the project.
    """
    if not "page" in kwargs.keys(): kwargs["page"] = "0"

    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/user2/public/search?result={str(kwargs['result'])}&page={str(kwargs['page'])}&query={str(kwargs['query'])}", verify=False).json()

def get_details_for_user(**kwargs):
    """
    A function used to get JSON user data inside the project.
    """

    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/user2/public/info/{str(kwargs['userId'])}", verify=False).json()

def list_high_scores_on_map(**kwargs):
    """
    A function used to get JSON highscore data inside the project.
    """

    return requests.get(f"https://tl3.shadowtree-software.se/TL3BackEnd/rest/highscore/public/{str(kwargs['mapId'])}?count={str(kwargs['count'])}", verify=False).json()
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.229 Whale/2.10.123.42 Safari/537.36",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
}

class WrongRequestError(Exception):
  def __init__(self, message):
    super().__init__(message)
  
class Riot:
  def __init__(self, api_key):
    headers['X-Riot-Token'] = api_key

  def match(self, **kwargs):  # MATCH-V5
    means = ['puuid', 'matchId']
    means = [i in kwargs for i in means]
    if sum(means) > 1:
      raise WrongRequestError('Multiple Options Found')
    elif means[0]:  # puuid
      url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{kwargs['puuid']}/ids?"
      for i in kwargs:
        if i == 'puuid':
          continue
        url += f"{i}={kwargs[i]}&"
    elif means[1]:  # matchId
      url=f"https://asia.api.riotgames.com/lol/match/v5/matches/{kwargs['matchId']}"
      if 'timeline' in kwargs:
        if kwargs['timeline']:
          url += '/timeline'
    else:
      raise WrongRequestError('No Option Found')
    res = requests.get(url, headers=headers)
    return res.json()

  def spectator(self, **kwargs):  # SPECTATOR-V4
    if 'summonerId' in kwargs:  # id
      url = f"https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{kwargs['summonerId']}"
    else:
      raise WrongRequestError('No Option Found')
    res = requests.get(url, headers=headers)
    return res.json()

  def summoner(self, **kwargs):  # SUMMONER-V4
    means = [i in kwargs for i in ['accountId', 'summonerName', 'puuid', 'summonerId']]
    if sum(means) > 1:
      raise WrongRequestError('Multiple Options Found')
    elif means[0]:  # accountId
      url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-account/{kwargs['accountId']}"
    elif means[1]:  # name
      url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{kwargs['summonerName']}"
    elif means[2]:  # puuid
      url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{kwargs['puuid']}"
    elif means[3]:  # id
      url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{kwargs['summonerId']}"
    else:
      raise WrongRequestError('No Option Found')
    res = requests.get(url, headers=headers)
    return res.json()
  

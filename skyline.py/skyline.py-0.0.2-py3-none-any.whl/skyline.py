"""
  The main file for most of the functionality of skyline.py

  ---

  Author: Yoshiboi18303 (Brice Coley)
  Support: https://discord.gg/ygK56KaxHC
"""

__author__ = "Yoshiboi18303"
__email__ = "yoshiboi18303.t@gmail.com"
__support__ = "https://discord.gg/ygK56KaxHC"

import aiohttp

def psc(client, client_id, api_key):
  if client is None:
    raise AttributeError("The client attribute was not found!")
  if client_id is None:
    raise AttributeError("The client_id attribute was not found!")
  if api_key is None:
    raise AttributeError("The api_key attribute was not found!")

  client_id = str(client_id)
  api_key = str(api_key)
  server_count = len(client.servers)

  url = "https://skylinebots.ml/api/bot/{}/stats".format(client_id)

  with aiohttp.request("POST", url, headers={
    "Authorization": api_key,
    "Content-Type": "application/json"
  }, body={
    "server_count": server_count
  }) as r:
    try:
      if r.ok:
        print("Successfully posted server stats to {}".format(url))
    except 299 > r.status >= 200:
      print("Code: {} | Text: {} - An error occurred while trying to post your server count. Please try again later.".format(r.status, r.statustext))

  def gwig(client_id):
    if client_id is None:
      raise AttributeError("The client_id attribute was not found!")

    url = "https://skylinebots.ml/api/bots/{}/widget".format(client_id)

    with aiohttp.request("GET", url, headers={}) as r:
      if r.ok:
        print("{} - Successful GET request! URL: {}".format(r.status, url))
      else:
        print("{} - Failed to finish the GET request... {}".format(r.status, r.statustext))
from Bitkub_Api import bitkub_api


api_key = 'YOUR_API_KEY'
api_secret = b'YOUR_API_SECRET'

bitkub = bitkub_api.Bitkub(api_key, api_secret)

print(bitkub.servertime())
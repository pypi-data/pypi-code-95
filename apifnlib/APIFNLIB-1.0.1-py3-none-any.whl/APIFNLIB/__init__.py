#Imports
import requests

#Offical Python Library For https://fn-api.com/ Made By LunakisLeaks [Creation Date: 10/9/2021]

class supLangs():
    #English
    English = 'en'
    en = 'en'
    ##############
    #Arabic
    Arabic = 'ar'
    ar = 'ar'
    ##############
    #Deutsch
    Deutsch = 'de'
    de = 'de'
    ##############
    #Spanish
    Spanish = 'es'
    es = 'es'
    #French
    French = 'fr'
    fr = 'fr'
    #Italian
    Italian = 'it'
    it = 'it'
    #Japanese
    Japanese = 'ja'
    ja = 'ja'
    #Korean
    Korean = 'ko'
    ko = 'ko'
    #Polish
    Polish = 'po'
    po = 'po'
    #Portuguese (Brazil)
    PortugueseBrazil = 'pt-BR'
    ptBR = 'pt-BR'
    #Russian
    Russian = 'ru'
    ru = 'ru'
    #Turkish
    Turkish = 'tr'
    tr = 'tr'

class NormalAPIEndpoints():
    #Host
    Host = "https://fn-api.com/"   
    #Blogposts
    Blogposts = 'https://fn-api.com/api/blogposts'
    #Calendar
    Calendar = 'https://fn-api.com/api/calendar'
    #Fortnite Status 
    FNStatus = 'https://fn-api.com/api/status'
    #Trello
    Trello = 'https://fn-api.com/api/trello'
    #Cloud Storage
    CloudStorage = 'https://fn-api.com/api/cloudstorage'
    #Cloud Storage [Selectable File]
    CloudStorageSelectableFile = 'https://fn-api.com/api/cloudstorage/'
    #Radio Sections
    RadioSections = 'https://fn-api.com/api/radios'
    #Emergency Notices
    EmergencyNotices = 'https://fn-api.com/api/emergencyNotices'
    #Backgrounds
    Backgrounds = ' https://fn-api.com/api/backgrounds'
    #News
    News = 'https://fn-api.com/api/news'
    #NewsType [Selectable GameMode]
    NewsType = 'https://fn-api.com/api/news/'
    #Playlists
    Playlists = 'https://fn-api.com/api/playlists'
    #ActivePlaylists 
    ActivePlaylists = 'https://fn-api.com/api/playlists/active'
    #SearchPlaylists [Selectable Playlist ID]
    SearchPlaylists = 'https://fn-api.com/api/playlists/'
    #ShopSections
    ShopSections = 'https://fn-api.com/api/shop/sections'
    #Stores 
    Stores = 'https://fn-api.com/api/stores'
    #Store [Selectable Store]
    Store = 'https://fn-api.com/api/stores/'
    #Stream [Selectable ID]
    Stream = 'https://fn-api.com/api/streams/'
    #AES
    AES = 'https://fn-api.com/api/aes'
    #Map
    Map = 'https://fn-api.com/api/map'
    #Raritys 
    Raritys = 'https://fn-api.com/api/rarity'
    #Cosmetics 
    Cosmetics = 'https://fn-api.com/api/cosmetics'
    #ShopSectionsList
    ShopSectionsList = 'https://fn-api.com/api/shop/sections/list'
    #Staging Servers
    Staging = 'https://fn-api.com/api/servers'

class PremAPIEndpoints():
    #Weapons
    Weapons = 'https://fn-api.com/api/weapons'
    #NPC
    NPC = 'https://fn-api.com/api/npcs'

def Calendar():
        requestCalendar = requests.get(f'{NormalAPIEndpoints.Calendar}')
        CalendarData = requestCalendar.json()
        return CalendarData
    
def FortniteStatus():
        requestFortniteStatus = requests.get(f'{NormalAPIEndpoints.FNStatus}')
        FortniteStatusData = requestFortniteStatus.json()
        return FortniteStatusData

def Trello():
        requestTrello = requests.get(f'{NormalAPIEndpoints.Trello}')
        TrelloData = requestTrello.json()
        return TrelloData

def CloudStorage():
        requestCloudStorage = requests.get(f'{NormalAPIEndpoints.CloudStorage}')
        CloudStorageData = requestCloudStorage.json()
        return CloudStorageData

def CloudStorageSelectableFile(fileName):
        requestCloudStorageSelectableFile = requests.get(f'{NormalAPIEndpoints.CloudStorageSelectableFile}?lang={fileName}')
        CloudStorageSelectableFileData = requestCloudStorageSelectableFile.json()
        return CloudStorageSelectableFileData

def RadioSections(translang="en"):
        requestRadioSections = requests.get(f'{NormalAPIEndpoints.RadioSections}?lang={translang}')
        RadioSectionsData = requestRadioSections.json()
        return RadioSectionsData

def Staging():
        requestEmergencyNotices = requests.get(f'{NormalAPIEndpoints.Staging}')
        EmergencyNoticesData = requestEmergencyNotices.json()
        return EmergencyNoticesData

def EmergencyNotices(translang="en"):
        requestEmergencyNotices = requests.get(f'{NormalAPIEndpoints.EmergencyNotices}?lang={translang}')
        EmergencyNoticesData = requestEmergencyNotices.json()
        return EmergencyNoticesData
    
def Backgrounds():
        requestBackgrounds = requests.get(f'{NormalAPIEndpoints.Backgrounds}')
        BackgroundsData = requestBackgrounds.json()
        return BackgroundsData

def News(translang="en"):
        requestNews = requests.get(f'{NormalAPIEndpoints.News}?lang={translang}')
        NewsData = requestNews.json()
        return NewsData

def NewsType(game_mode,translang="en"):
        requestNewsType = requests.get(f'{NormalAPIEndpoints.NewsType}{game_mode}?lang={translang}')
        NewsTypeData = requestNewsType.json()
        return NewsTypeData

def Playlists(translang="en"):
        requestPlaylists = requests.get(f'{NormalAPIEndpoints.Playlists}?lang={translang}')
        PlaylistsData = requestPlaylists.json()
        return PlaylistsData
    
def ActivePlaylists(translang="en"):
        requestActivePlaylist = requests.get(f'{NormalAPIEndpoints.ActivePlaylists}?lang={translang}')
        ActivePlaylistData = requestActivePlaylist.json()
        return ActivePlaylistData

def SearchPlaylists(playlistid):
        requestSearchPlaylist = requests.get(f'{NormalAPIEndpoints.SearchPlaylists}{playlistid}')
        SearchPlaylistData = requestSearchPlaylist.json()
        return SearchPlaylistData

def ShopSections(translang="en"):
        ShopSections = requests.get(f'{NormalAPIEndpoints.ShopSections}?lang={translang}')
        ShopSectionsData = ShopSections.json()
        return ShopSectionsData

def Stores(translang="en"):
        requestStores = requests.get(f'{NormalAPIEndpoints.Stores}?lang={translang}')
        StoresData = requestStores.json()
        return StoresData
    
def Store(storename):
        requestStore = requests.get(f'{NormalAPIEndpoints.Store}{storename}')
        StoreData = requestStore.json()
        return StoreData

def Stream(stream_id,translang="en"):
        requestStream = requests.get(f'{NormalAPIEndpoints.Stream}{stream_id}?lang={translang}')
        StreamData = requestStream.json()
        return StreamData

def AES():
        requestAES = requests.get(f'{NormalAPIEndpoints.AES}')
        AESData = requestAES.json()
        return AESData
    
def Map(translang="en"):
        requestMap = requests.get(f'{NormalAPIEndpoints.AES}?lang={translang}')
        MapData = requestMap.json()
        return MapData
    
def Raritys(translang="en"):
        requestRaritys = requests.get(f'{NormalAPIEndpoints.Raritys}?lang={translang}')
        RaritysData = requestRaritys.json()
        return RaritysData

def Cosmetics():
        requestCosmetics = requests.get(f'{NormalAPIEndpoints.Cosmetics}')
        CosmeticsData = requestCosmetics.json()
        return CosmeticsData

def ShopSectionsList(translang="en"):
        requestShopSectionsList = requests.get(f'{NormalAPIEndpoints.ShopSectionsList}?lang={translang}')
        ShopSectionsListData = requestShopSectionsList.json()
        return ShopSectionsListData
        
def Weapons(authorization,translang="en"):
        requestWeapons = requests.get(f'{PremAPIEndpoints.Weapons}?lang={translang}')
        header = {
          'Authorization': f'{authorization}'
        }
        WeaponsData = requests.get(requestWeapons, headers=header).json()
        return WeaponsData

def NPC(authorization,translang="en"):
        requestNPC = requests.get(f'{PremAPIEndpoints.NPC}?lang={translang}')
        header = {
          'Authorization': f'{authorization}'
        }
        NPCData = requests.get(requestNPC, headers=header).json()
        return NPCData

def apiStatus():
        class StatusStrings:
                requestAPI = requests.get(f'{NormalAPIEndpoints.Host}')
                Status = requestAPI.status_code
                if Status == 200:
                        print(f'API Status: Up | Status Code: ', end="")
                else:
                        print('API Status: Down | Status Code: ', end="")
        return StatusStrings.Status

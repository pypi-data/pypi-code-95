import discord, os, os.path, socket
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from discord.ext import commands
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class discbot:
    def init(prefix,removehelp = False):
        client = discord.Client()
        client = commands.Bot(command_prefix = prefix)
        if (removehelp == True):
            client.remove_command("help")
        
        @client.event
        async def on_ready():
            print('Logged in as {0.user}'.format(client))
            while True:
                if True:
                    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for commands!"))
        
        return client

class googless():
    def init(SCOPES):
        '''
        SCOPES: Which scope you want to use, either https://www.googleapis.com/auth/spreadsheets or https://www.googleapis.com/auth/spreadsheets.readonly \n
        ''' 
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
    
    def batchval(SPREADSHEET_ID,BATCH_RANGE_NAME,creds):
        """
        SPREADSHEET_ID: Your spreadsheet ID \n
        BATCH_RANGE_NAME: The range name for all of your cells you want to read (batch read)
        """
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=BATCH_RANGE_NAME).execute()
        values = result.get('values', [])
        return (service,sheet,result,values)

    class tools():
        def getBatch(SPREADSHEET_ID,service,RANGE_NAME_LIST,VALUE_RENDER_OPTION = "FORMATTED_VALUE",DATETIME_RENDER_OPTION = "FORMATTED_STRING"):
            '''
            RANGE_NAME_LIST: A list of all the ranges you want to read \n
            VALUE_RENDER_OPTION: (optional) Research what this is
            DATETIME_RENDER_OPTION: (optional) Research what this is
            '''
            request = service.spreadsheets().values().batchGet(spreadsheetId=SPREADSHEET_ID,ranges=RANGE_NAME_LIST,valueRenderOption=VALUE_RENDER_OPTION,dateTimeRenderOption=DATETIME_RENDER_OPTION)
            response = request.execute()
            return str(response)

        def clearBatch(service,SPREADSHEET_ID,BATCH_RANGE_NAME):
            request = service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range=BATCH_RANGE_NAME,body={"range" : BATCH_RANGE_NAME})
            response = request.execute()
            return str(response)
        
        def getSub(ORIGIN_STRING,STARTDEF,ENDDEF):
            start = ORIGIN_STRING.find(STARTDEF) + len(STARTDEF)
            end = ORIGIN_STRING.find(ENDDEF)
            return str(ORIGIN_STRING[start:end])

class gui:
    def init(width,height,caption = "DEFAULT",background_colour = (255,255,255)):
        screen = pygame.display.set_mode((width, height))
        pygame.display.flip()
        pygame.display.set_caption(caption)
        screen.fill(background_colour)
        return screen

class gpt:
    class sockets:
        def server(ip,port,queue):
            while True:
                #sock sends
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = (ip, port)
                sock.bind(server_address)
                sock.listen(queue)
                connection, client_address = sock.accept()
                return (sock,connection,client_address)

        def client(ip,port):
            while True:
                #sock sends
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = (ip, port)
                sock.connect(server_address)
                return sock
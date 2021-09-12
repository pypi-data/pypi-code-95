from __future__ import print_function
import httplib2
import os, io
from apiclient import discovery
#from oauth2client import client
from oauth2client import tools
#from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
from . import auth
import requests
import json

class Drive:
        
    def __init__(self, SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME, CREDENTIAL_DIR = None):
        self.SCOPES = SCOPES
        self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
        self.APPLICATION_NAME = APPLICATION_NAME
        self.CREDENTIAL_DIR = CREDENTIAL_DIR
        self.__authenticate()

    def list_drives(self, size = None, useDomainAdminAccess = False):
        results = self.drive_service.drives().list(
                                                    pageSize=size,
                                                    useDomainAdminAccess = useDomainAdminAccess
                                                    ).execute()
        print(results)
        items = results.get('teamDrives', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))


    def __authenticate(self):
        self.authInst = auth.auth(self.SCOPES, self.CLIENT_SECRET_FILE, self.APPLICATION_NAME, self.CREDENTIAL_DIR)
        self.credentials = self.authInst.getCredentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.drive_service = discovery.build('drive', 'v3', http=self.http)

    def listFiles(self, size):
        results = self.drive_service.files().list(
                                                    pageSize=size,
                                                    fields="nextPageToken, files(id, name)"
                                                ).execute()     
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))

    def uploadFile(self, filename, filepath, mimetype):
        file_metadata = {'name': filename}
        media = MediaFileUpload(    filepath,
                                    mimetype=mimetype)
        file = self.drive_service.files().create(   
                                                    body=file_metadata,
                                                    media_body=media,
                                                    fields='id'
                                                ).execute()
        print('File ID: %s' % file.get('id'))

    def updateFileParent(self, file_id, addParents, idFolder = None):
        response = self.drive_service.files().update(   
                                                        fileId = file_id, 
                                                        supportsAllDrives = True,
                                                        removeParents = idFolder,
                                                        addParents = addParents
                                                    ).execute()
        return response

    #Download Google Docs files
    def downloadFile(self, file_id,filepath):

        request = self.drive_service.files().export_media(fileId=file_id,mimeType='text/csv')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        with io.open(filepath,'wb') as f:
            fh.seek(0)
            f.write(fh.read())

    #Download anything but Google Docs or binary files
    def download(self, id, nome, extension = 'pdf', path='./pdfs', encoding = None):
        if encoding == None:
            encoding = "utf-8"
        url = f"https://www.googleapis.com/drive/v3/files/{id}?alt=media"
        token = self.__get_token()
        payload={}
        headers = {
            'Authorization': f'Bearer {token}'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if not os.path.exists(path):
                os.makedirs(path)
            with open(f'{path}/{nome}.{extension}', 'wb') as f:
                f.write(response.content)
            return True
        except:
            print(f'errors while download file {nome}')
            return False

    def __get_token(self):
        
        with open("./.credentials/google-drive-credentials.json") as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()

        return jsonObject['access_token']

    def createFolder(self, name, supportsAllDrives = False):
        file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.drive_service.files().create(   body=file_metadata,
                                                    fields='id',
                                                    supportsAllDrives = supportsAllDrives
                                                ).execute()
        print ('Folder ID: %s' % file.get('id'))

    #   to get shared drives files you need to pass includeItemsFromAllDrives and supportsAllDrives = True
    #   and corpora = 'drive' or 'allDrives'
    def searchFile(self, size, query, corpora = 'user', includeItemsFromAllDrives = False, supportsAllDrives = False, driveId = None):
        results = self.drive_service.files().list(
                                                    pageSize = size,
                                                    fields = "nextPageToken, files(id, name, kind, mimeType)",
                                                    q = query,
                                                    corpora = corpora, 
                                                    includeItemsFromAllDrives = includeItemsFromAllDrives, 
                                                    supportsAllDrives = supportsAllDrives
                                                ).execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
            return None
        return items

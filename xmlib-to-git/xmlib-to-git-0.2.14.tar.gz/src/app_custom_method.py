
# -*- coding: utf-8 -*-
import binascii
import os, re
import base64
from src.utils import my_tools


class CustomMethod(object):
    """
    Define a custom method
    """
    get = ""
    post = ""
    put = ""
    patch = ""

    def __init__(self, method, dir):
        self.id = method["id"]
        self.name = method.Name.cdata
        if hasattr(method, "GetB64"):
            self.get = method.GetB64.cdata
        if hasattr(method, "PostB64"):
            self.post = method.PostB64.cdata
        if hasattr(method, "PutB64"):
            self.put = method.PutB64.cdata
        if hasattr(method, "PatchB64"):
            self.patch = method.PatchB64.cdata
        self.endpoint = method.Endpoint.cdata
        self.method_dir = "{}/{}".format(dir, self.endpoint)

    def to_file(self):
        # properties file
        if not os.path.exists(self.method_dir):
            os.makedirs(self.method_dir)
        file = open("{}/PROPERTIES.md".format(self.method_dir), 'w+', encoding='utf-8')
        with file:
            # nom de l'objet
            file.write("# {}\n".format(self.name))
            # Informations
            file.write("\n\n## Informations\n")
            file.write("- id : {}\n".format(self.id))
            file.write("- endpoint : <server_prod_url>/api2/custom/{}\n".format(self.endpoint))

        if self.get:
            file = open("{}/get.js".format(self.method_dir), 'w+', encoding='utf-8')
            with file:
                file_content = base64.b64decode(self.get).decode("UTF-8", "ignore")
                file.write(file_content)

        if self.post:
            file = open("{}/post.js".format(self.method_dir), 'w+', encoding='utf-8')
            with file:
                file_content = base64.b64decode(self.post).decode("UTF-8", "ignore")
                file.write(file_content)

        if self.put:
            file = open("{}/put.js".format(self.method_dir), 'w+', encoding='utf-8')
            with file:
                file_content = base64.b64decode(self.put).decode("UTF-8", "ignore")
                file.write(file_content)

        if self.patch:
            file = open("{}/patch.js".format(self.method_dir), 'w+', encoding='utf-8')
            with file:
                file_content = base64.b64decode(self.patch).decode("UTF-8", "ignore")
                file.write(file_content)


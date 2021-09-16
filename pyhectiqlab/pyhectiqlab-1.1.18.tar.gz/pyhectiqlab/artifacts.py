import requests
import os
import time
import pyhectiqlab.ops as ops
from pyhectiqlab.auth import AuthProvider

class SharedArtifactsManager():
    def __init__(self):
        self.auth_provider = AuthProvider()

    def list_projects(self):
        if self.auth_provider.is_logged()==False:
            print("User is not authentificated.")
            return
        projects = ops.get_all_projects(token=self.auth_provider.secret_api_key)
        if len(projects["result"])==0:
            print("No projects.")
        else:
            for project in projects["result"]:
                print(f"[{project['id']}] {project['name']}")

    def list_artifacts(self, project_id: str):
        if self.auth_provider.is_logged()==False:
            print("User is not authentificated.")
            return
        return ops.list_shared_artifacts(project_id, token=self.auth_provider.secret_api_key)

    def select_artifact(self, project_id: str):
        if self.auth_provider.is_logged()==False:
            print("User is not authentificated.")
            return
        print("Listing artifacts...")
        artifacts = ops.list_shared_artifacts(project_id, token=self.auth_provider.secret_api_key)
        print("Artifacts fetched.\n")
        if len(artifacts["results"])==0:
            print("No artifacts.")
            return

        print("Select an artifact: ")
        for i,artifact in enumerate(artifacts["results"]):
            # print(i, artifact)
            print(f" [{i}] {artifact['name']}")

        index = input("Index: ")
        try:
            if int(index)>=len(artifacts["results"]):
                print("Invalid input.")
                return
        except:
            print("Invalid input.")
            return

        artifact = artifacts["results"][int(index)]
        download_path = input("Enter download path [default ./]: ")
        if download_path=="":
            download_path = "./"

        print("Downloading ...")

        res = ops.get_shared_artifacts_download_link(artifact["uuid"], token=self.auth_provider.secret_api_key)
        url = res["url"]

        res = requests.get(url)
        savepath = os.path.join(os.path.abspath(download_path), artifact["name"])
        open(savepath, "wb").write(res.content)
        print(f"Saved at {savepath}")
        return

    def push_artifact(self, filepath: str, project_id:str):
        if self.auth_provider.is_logged()==False:
            print("User is not authentificated.")
            return
        filename = os.path.basename(filepath)
        num_bytes = os.path.getsize(filepath)
        content_bytes = open(filepath, "rb")

        return ops.add_shared_artifact(project_id=project_id, 
                                        filename=filename, 
                                        filepath=filepath,
                                         num_bytes=num_bytes, 
                                         token=self.auth_provider.secret_api_key)
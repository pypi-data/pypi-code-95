import os
import json
import requests
import http
import zipfile
from requests_toolbelt.multipart.encoder import MultipartEncoder

REGISTER_ENDPOINT = 'register'
LOGIN_ENDPOINT = 'login'
MODELS_ENDPOINT = 'models'
TRAINING_REQUESTS_ENDPOINT = 'trainingrequests'
INFERENCE_ENDPOINT = 'inferences'
DATASETS_ENDPOINT = 'datasets'
VERSIONS_ENDPOINT = 'versions'
LABELS_ENDPOINT = 'labels'
APPLICATIONS_ENDPOINT = 'applications'

ID = "id"

class Client():
  """ 
  Client class to interact with the SeeMe.ai backend, allowing you to manage models, datasets, predictions and training requests.
  
  Parameters:
  ---
  
  username (optional) : the username for the account you want to use;
  apikey (optional) : the API key for the username you want user.

  Note: 
  username and apikey are optional but they need to used together in order to be authenticated. Authentication will be used on subsequent requests.
  Alternatively, you can use the login method (see below)
  """
  def __init__(self, username:str=None, apikey:str=None, backend:str="https://api.seeme.ai/api/v1/"):
    self.backend = backend
    self.headers = {}
    self.username = username
    self.update_auth_header(username, apikey)
    self.endpoints = {
      REGISTER_ENDPOINT: self.crud_endpoint(REGISTER_ENDPOINT),
      LOGIN_ENDPOINT: self.crud_endpoint(LOGIN_ENDPOINT),
      MODELS_ENDPOINT: self.crud_endpoint(MODELS_ENDPOINT),
      TRAINING_REQUESTS_ENDPOINT: self.crud_endpoint(TRAINING_REQUESTS_ENDPOINT),
      INFERENCE_ENDPOINT: self.crud_endpoint(INFERENCE_ENDPOINT),
      DATASETS_ENDPOINT: self.crud_endpoint(DATASETS_ENDPOINT),
      APPLICATIONS_ENDPOINT: self.crud_endpoint(APPLICATIONS_ENDPOINT)
    }
    self.applications = []

  # -- Login / Registration --

  def register(self, username:str, email:str, password:str, firstname:str, name:str):
    """  
    Register a new user with a username, email and password. 
    
    Optionally, you can add a first and last name.
    """
    register_api = self.endpoints[REGISTER_ENDPOINT]
    register_data = {
      'username': username,
      'email': email,
      'password': password,
      'firstname': firstname,
      'name': name,
    }

    r = requests.post(register_api, data=json.dumps(register_data), headers=self.headers)

    registered_user = r.json()

    if "message" in registered_user:
      raise ValueError(registered_user["message"])
    
    return registered_user

  def login(self, username:str, password:str):
    """ 
    Log in with a username and password.
    
    The username and password will be used to get the API key from the backend. 
    The method will fail if the user is not known, the password is incorrect, or the service cannot be reached.
    """
    login_api = self.endpoints[LOGIN_ENDPOINT]
    login_data = {
      'username': username,
      'password': password
    }
    
    logged_in = self.api_post(login_api, login_data)

    username = logged_in["username"]
    apikey = logged_in["apikey"]

    user_id = logged_in["id"]

    self.update_auth_header(username, apikey)
    self.username = username
    self.user_id = user_id

    applications_api = self.endpoints[APPLICATIONS_ENDPOINT]
    self.applications =  self.api_get(applications_api)

    return logged_in
      
  def logout(self):
    """ Log out the current user."""
    self.update_auth_header("", "")

  def get_application_id(self, base_framework="pytorch", framework="", base_framework_version="1.8.1", framework_version="", application="image_classification"):
    """ Returns the application_id for the application you want to deploy:
    
    Parameters
    ---

    base_framework: the base_framework for the application (e.g. "pytorch", ...)
    base_framework_version: the version of the base_framework (e.g. "1.9.0", ...)
    framework: the framework for the application (e.g. "fastai", ...)
    framework_version: the version of the framework (e.g. "2.5.2", ...)
    application: the type of application you want to deply (e.g. "image_classification", "object_detection", "text_classification", "structured")

    Note
    ---

    To get a list of all the supported applications, see the "get_applications" method.
    """
    if self.applications == []:
      self.applications = self.get_applications()

    for f in self.applications:
      if f["base_framework"] == base_framework \
        and f["framework"] == framework \
        and f["base_framework_version"] == base_framework_version \
        and f["framework_version"] == framework_version \
        and f["application"] == application:
          return f["id"]
    
    for f in self.applications:
      if f["base_framework"] == base_framework \
        and f["framework"] == framework \
        and f["base_framework_version"] in base_framework_version \
        and f["framework_version"] == framework_version \
        and f["application"] == application:
          return f["id"]
      
    raise NotImplementedError
    
  # -- CRUD models --

  def get_models(self):
    self.requires_login()

    model_api = self.endpoints[MODELS_ENDPOINT]

    return self.api_get(model_api)

  def create_model(self, model):
    self.requires_login()

    if not "auto_convert" in model:
      model["auto_convert"] = True

    model_api = self.endpoints[MODELS_ENDPOINT]

    return self.api_post(model_api, model)

  def get_model(self, model_id:str):
    self.requires_login()

    model_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id

    return self.api_get(model_api)

  def update_model(self, model):
    self.requires_login()

    assert model
    assert model[ID]
    model_api = self.endpoints[MODELS_ENDPOINT] + "/" + model[ID]
    return self.api_put(model_api, model)

  def delete_model(self, model_id:str):
    self.requires_login()
    delete_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id

    return self.api_delete(delete_api)

  def upload_model(self, model_id:str, folder:str="data", filename:str="export.pkl"):

    model_upload_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id  + "/upload"

    return self.upload(model_upload_api, folder, filename, 'application/octet-stream')
  
  def upload_logo(self, model_id:str, folder:str="data", filename:str="logo.jpg"):
    if filename.endswith("jpg"):
      content_type="image/jpg"
    elif filename.endswith("jpeg"):
      content_type="image/jpeg"
    elif filename.endswith("png"):
      content_type="image/png"

    model_upload_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id  + "/upload"

    return self.upload(model_upload_api, folder, filename,  content_type)
  
  def get_logo(self, model):
    logo_endpoint = self.endpoints[MODELS_ENDPOINT] + "/" + model["id"] + "/download/logo"
    return self.api_download(logo_endpoint, model["logo"])

  
  def download_active_model(self, model, assetType="pkl"):
    """
      assetType: mlmodel, tflite, onnx, pkl, labels, names
    """

    if assetType not in ["pkl", "mlmodel", "tflite", "onnx", "names", "labels"]:
      raise NotImplementedError

    model_endpoint = self.endpoints[MODELS_ENDPOINT] + "/" + model["id"] + "/download/" + assetType

    extension = assetType

    if assetType == "labels":
      extension = "txt"

    return self.api_download(model_endpoint, model["active_version_id"]+"." + extension)

  def upload(self, url:str, folder:str, filename:str, content_type:str):
    self.requires_login()

    data = MultipartEncoder(
                fields={
                    'file': (filename, open(folder + "/" + filename, 'rb'), content_type)}
                       )

    content_headers = self.headers

    content_headers['Content-Type'] = data.content_type

    return self.api_upload(url, data=data, headers=content_headers)

  # -- CRUD Model Versions

  def get_model_versions(self, model_id):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{VERSIONS_ENDPOINT}"

    return self.api_get(model_version_api)

  def get_model_version(self, model_id, version_id):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{VERSIONS_ENDPOINT}/{version_id}"

    return self.api_get(model_version_api)

  def create_model_version(self, model_id, version):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{VERSIONS_ENDPOINT}"

    return self.api_post(model_version_api, version)
  
  def update_model_version(self, version):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{version['model_id']}/{VERSIONS_ENDPOINT}/{version['id']}"

    return self.api_put(model_version_api, version)

  def delete_model_version(self, model_id, version_id):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{VERSIONS_ENDPOINT}/{version_id}"

    return self.api_delete(model_version_api)

  def upload_model_version(self, version, folder:str="data", filename:str="export.pkl"):

    model_version_upload_api = self.endpoints[MODELS_ENDPOINT] + "/" + version['model_id']  + "/"+ VERSIONS_ENDPOINT + "/" + version["id"] + "/upload"

    return self.upload(model_version_upload_api, folder, filename, 'application/octet-stream')

  def upload_model_version_logo(self, model_id, version_id, folder:str="data", filename:str="logo.jpg"):
    if filename.endswith("jpg"):
      content_type="image/jpg"
    elif filename.endswith("jpeg"):
      content_type="image/jpeg"
    elif filename.endswith("png"):
      content_type="image/png"

    model_version_upload_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id  + "/"+ VERSIONS_ENDPOINT + version["id"] + "/upload"

    return self.upload(model_version_upload_api, folder, filename, content_type)
  
  def download_version(self, version, assetType):
    """
      assetType: mlmodel, tflite, onnx, pkl, labels, names
    """

    if assetType not in ["pkl", "mlmodel", "tflite", "onnx", "names", "labels"]:
      raise NotImplementedError()

    extension = assetType

    if assetType == "labels":
      extension = "txt"

    version_endpoint = self.endpoints[MODELS_ENDPOINT] + "/" + version["model_id"] + "/" + VERSIONS_ENDPOINT + "/" + version["id"] + "/download/" + assetType
    return self.api_download(version_endpoint, version["id"]+"." + extension)
  
  # -- CRUD requests --

  def get_training_requests(self, applicationId="", started="", finished=""):
    self.requires_login()

    training_requests_api = self.endpoints[TRAINING_REQUESTS_ENDPOINT]

    if applicationId != "":
      training_requests_api += f"?applicationId={applicationId}&started={started}&finished={finished}"

    return self.api_get(training_requests_api)
  
  def create_training_request(self, version):
    self.requires_login()

    req_api = self.endpoints[TRAINING_REQUESTS_ENDPOINT]
    req_data = {
      'dataset_id': version["dataset_id"],
      'dataset_version_id': version["id"]
    }

    return self.api_post(req_api, req_data)

  def update_training_request(self, training_request):
    self.requires_login()

    assert training_request
    assert training_request[ID]
    training_request_api = self.endpoints[TRAINING_REQUESTS_ENDPOINT] + "/" + training_request[ID]
    return self.api_put(training_request_api, training_request)

  def delete_training_request(self, id:str):
    self.requires_login()
    delete_api = self.endpoints[TRAINING_REQUESTS_ENDPOINT] + "/" + id

    return self.api_delete(delete_api)

  # -- CRUD Inference --

  def predict(self, model_id:str, folder:str, item, input_type="image_classification"):
      return self.inference(model_id, folder, item, input_type)

  def inference(self, model_id:str, folder:str, item, input_type="image_classification"):
    self.requires_login()

    inference_api = self.endpoints[INFERENCE_ENDPOINT] + "/" + model_id

    if input_type=="image_classification":
      data = MultipartEncoder(
                  fields={
                      'file': (item, open(f"{folder}/{item}", 'rb'), 'application/octet-stream')}
                        )

      content_headers = self.headers

      content_headers['Content-Type'] = data.content_type

      return self.api_upload(inference_api, data=data, headers=content_headers)
    elif input_type=="text_classification":
      data = {
        'input_text': item
      }

      return self.api_post(inference_api, data)
    elif input_type=="structured":
      data = {
              'input_text': item
      }

      return self.api_post(inference_api, data)
    else:
      raise NotImplementedError

  def version_inference(self, version, folder:str, item, input_type="image_classification"):
    self.requires_login()

    inference_api = self.endpoints[INFERENCE_ENDPOINT] + "/" + version['model_id'] + "/" + VERSIONS_ENDPOINT + "/" + version['id']

    if input_type=="image_classification":
      data = MultipartEncoder(
                  fields={
                      'file': (item, open(f"{folder}/{item}", 'rb'), 'application/octet-stream')}
                        )

      content_headers = self.headers

      content_headers['Content-Type'] = data.content_type

      return self.api_upload(inference_api, data=data, headers=content_headers)
    elif input_type=="text_classification":
        data = {
          'input_text': item
        }

        return self.api_post(inference_api, data)
    elif input_type=="structured":
      data = {
              'input_text': item
      }

      return self.api_post(inference_api, data)
    else:
      raise NotImplementedError

  def update_inference(self, inference):
    self.requires_login()

    inference_api = self.endpoints[INFERENCE_ENDPOINT] + "/" + inference["id"]

    return self.api_put(inference_api, inference)

  # -- CRUD applicationS --
  def get_applications(self):
    self.requires_login()

    application_api = self.endpoints[APPLICATIONS_ENDPOINT]

    return self.api_get(application_api)

  # -- CRUD DATASETS --

  def get_datasets(self):
    self.requires_login()

    dataset_api = self.endpoints[DATASETS_ENDPOINT]

    return self.api_get(dataset_api)

  def create_dataset(self, dataset):
    self.requires_login()

    dataset_api = self.endpoints[DATASETS_ENDPOINT]

    return self.api_post(dataset_api, dataset)

  def get_dataset(self, dataset_id:str):
    self.requires_login()

    dataset_api = self.endpoints[DATASETS_ENDPOINT] + "/" + dataset_id

    return self.api_get(dataset_api)

  def update_dataset(self, dataset):
    self.requires_login()

    assert dataset
    assert dataset[ID]
    dataset_api = self.endpoints[DATASETS_ENDPOINT] + "/" + dataset[ID]
    return self.api_put(dataset_api, dataset)

  def delete_dataset(self, id:str):
    self.requires_login()
    dataset_api = self.endpoints[DATASETS_ENDPOINT] + "/" + id

    return self.api_delete(dataset_api)

  def create_dataset_version(self, dataset_id, dataset_version):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}"

    return self.api_post(dataset_version_api, dataset_version)

  def get_dataset_versions(self, dataset_id):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}"

    return self.api_get(dataset_version_api)
  
  def get_dataset_version(self, dataset_id, version_id):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}"

    return self.api_get(dataset_version_api)

  def update_dataset_version(self, dataset_id, dataset_version):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version['id']}"

    return self.api_put(dataset_version_api, dataset_version)

  def delete_dataset_version(self, dataset_id, dataset_version):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version['id']}"

    return self.api_delete(dataset_version_api)
  
  def create_label(self, dataset_id, version_id, label):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/labels"

    return self.api_post(labels_api, label)

  def get_labels(self, dataset_id, version_id):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/labels"

    return self.api_get(labels_api)
  
  def get_label(self, dataset_id, version_id, label_id):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/labels/{label_id}"

    return self.api_get(labels_api)

  def update_label(self,  dataset_id, version_id, label):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/labels/{label['id']}"

    return self.api_put(labels_api, label)

  def delete_label(self, dataset_id, version_id, label):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/labels/{label['id']}"

    return self.api_delete(labels_api)
  
  def create_split(self, dataset_id, version_id, split):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/splits"

    return self.api_post(splits_api, split)

  def get_splits(self, dataset_id, version_id):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/splits"

    return self.api_get(splits_api)
  
  def get_split(self, dataset_id, version_id, split_id):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/splits/{split_id}"

    return self.api_get(splits_api)

  def update_split(self,  dataset_id, version_id, split):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/splits/{split['id']}"

    return self.api_put(splits_api, split)

  def delete_split(self, dataset_id, version_id, split):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/splits/{split['id']}"

    return self.api_delete(splits_api)
  
  def get_items(self, dataset_id, version_id, params=None):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/items"

    return self.api_get(items_api, params=params)

  def create_item(self, dataset_id, version_id, item):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/items"

    return self.api_post(items_api, item)

  def get_item(self, dataset_id, version_id, item_id):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/items/{item_id}"

    return self.api_get(items_api)

  def update_item(self,  dataset_id, version_id, item):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/items/{item['id']}"

    return self.api_put(items_api, item)

  def delete_item(self, dataset_id, version_id, split_id, item):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/splits/{split_id}/items/{item['id']}"

    return self.api_delete(items_api)

  def upload_item_image(self, dataset_id, version_id, item_id, folder, filename):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/items/{item_id}/upload"
    
    if filename.endswith("jpg"):
      content_type="image/jpg"
    elif filename.endswith("jpeg"):
      content_type="image/jpeg"
    elif filename.endswith("png"):
      content_type="image/png"
    else:
      print("Image type not supported")
      return

    data = MultipartEncoder(
                fields={
                    'file': (filename, open(folder + "/" + filename, 'rb'), content_type)}
                       )

    content_headers = self.headers

    content_headers['Content-Type'] = data.content_type

    return self.api_upload(items_api, data=data, headers=content_headers)

  def download_item_image(self, dataset_id, version_id, item_id, download_location, thumbnail=False):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/items/{item_id}/download"
  
    if thumbnail:
      items_api += "?thumbnail=true"

    return self.api_download(items_api, download_location)

  def download_dataset(self, dataset_id, version_id, split_id="", extract_to_dir="data", download_file="dataset.zip", remove_download_file=True):
    self.requires_login()

    dataset_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/download"

    if split_id != "":
      dataset_api = f"{dataset_api}/{split_id}"

    self.api_download(dataset_api, download_file)

    with zipfile.ZipFile(download_file, 'r') as zip_ref:
      zip_ref.extractall(extract_to_dir)
    
    if remove_download_file:
      os.remove(download_file)
    
  def upload_dataset_version(self, dataset_id, version_id, folder="data", filename="dataset.zip"):
    self.requires_login()

    dataset_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{version_id}/upload"

    content_type="application/x-zip-compressed"

    data = MultipartEncoder(
                fields={
                    'file': (filename, open(folder + "/" + filename, 'rb'), content_type)}
                       )

    content_headers = self.headers

    content_headers['Content-Type'] = data.content_type

    return self.api_upload(dataset_api, data=data, headers=content_headers)

  def import_yolo_dataset(self, dataset_name="yolo import", split_names=["train", "test"], folder="data", names_filename="yolo.names", config_filename="config.json"):
    self.requires_login()
    
    dataset = {
      "name": dataset_name,
      "multi_annotation": True
    }

    dataset = self.create_dataset(dataset)

    version = dataset["versions"][0]

    d_id = dataset["id"]
    v_id = version["id"]

    config = {}
    labels = {}

    config_fullpath = f"{folder}/{config_filename}"

    if os.path.exists(config_fullpath):
      with open(config_fullpath) as config_file:
        config = json.load(config_file)

    with open(f"{folder}/{names_filename}") as names_file:
      names = names_file.readlines()
      index = 0

      for label_name in names:
        label_name = label_name.strip()
        label_color = ""

        if "colors" in config:
          label_color = config["colors"][label_name] if label_name in config["colors"] else random_color()
        else:
          label_color = random_color()

        label = {
          "name": label_name,
          "color": label_color
        }

        label = self.create_label(d_id, v_id, label)
        labels[str(index)] = label
        index += 1

    for split_filename in split_names:
      split = {
        "name": split_filename
      }

      split = self.create_split(d_id, v_id, split)

      with open(f"{folder}/{split_filename}.txt") as split_file:
        split_items = split_file.readlines()
        for item_filename in split_items:
          item_filename = item_filename.strip()

          file_split = os.path.splitext(item_filename)
          item_name = file_split[0]
          item_extension = file_split[1]

          local_item = {
            "name": item_name,
            "extension": item_extension,
            "splits": [split],
            "annotations": []
          }

          with open(f"{folder}/{item_name}.txt") as annotation_file:
            annotation_lines = annotation_file.readlines()

            for annotation_line in annotation_lines:
              annotation_line = annotation_line.strip()

              annotation_split = annotation_line.split(" ")

              label_index = annotation_split[0]

              label = labels[label_index]

              coords = " ".join(annotation_split[1:])

              annotation = {
                "label_id": label["id"],
                "coordinates": coords
              }

              local_item["annotations"].append(annotation)
            
            item = self.create_item(d_id, v_id, local_item)

            self.upload_item_image(d_id, v_id, item["id"], folder, item_filename)
    return dataset

  # Convenience methods

  def get_apikey(self):
    return self.apikey
  
  def random_color():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    rgb = (r,g,b)

    return '#%02x%02x%02x' % rgb

  # Helpers

  def requires_login(self):
    if not self.is_logged_in():
      raise Exception("You need to be logged in for this.")

  def update_applications(self):
    self.applications = get_applications()

  def update_auth_header(self, username:str=None, apikey:str=None):
    if username == None or apikey == None:
      return

    self.apikey = apikey
    
    self.headers = {
      "Authorization": f"{username}:{apikey}"
    }
  
  def is_logged_in(self):
    if "Authorization" in self.headers:
      return True

    return False

  def crud_endpoint(self, endpoint:str):
    return f"{self.backend}{endpoint}"

  ## CRUD API methods

  def api_get(self, api:str, params=None):
    r = requests.get(api, headers=self.headers, params=params)

    return r.json()

  def api_post(self, api:str, data):
    data = json.dumps(data)

    r = requests.post(api, data=data, headers=self.headers)
    
    return r.json()
  
  def api_upload(self, api:str, data, headers):
    r = requests.post(api, data=data, headers=headers)
    
    return r.json()
  
  def api_put(self, api:str, data):
    data = json.dumps(data)

    r = requests.put(api, data=data, headers=self.headers)

    return r.json()
  
  def api_delete(self, api:str):
    r = requests.delete(api, headers=self.headers)

    return r.json()

  def api_download(self, api:str, filename:str):
    r = requests.get(api, allow_redirects=True, headers=self.headers)

    open(filename, "wb").write(r.content)
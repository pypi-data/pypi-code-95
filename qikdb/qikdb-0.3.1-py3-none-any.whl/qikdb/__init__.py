__version__ = '0.3.1'

import json
import os
import termcolor
from os import path
from termcolor import colored


class DB:
  """
  Creates a new instance of a database.
  name = 'myName'
  """

  def __init__(self, **kwargs):
    """
    Initializes new instance of database. (Do not call as script).
    """
    if kwargs == {} or kwargs['config'] == {}:
      self.name = "myDB";
      self.directory = "./";
      self.path = f"{self.directory}{self.name}";
    else:
      if not kwargs["config"]["name"] == None:
        self.name = kwargs['config']['name']
      else:
        self.name = "myDB";
      
      if not kwargs["config"]["directory"] == None:
        self.directory = kwargs["config"]["directory"];
      else:
        self.directory = "./";


      self.path = f"{self.directory}/{self.name}.json";
    self.__createFile__()
    
  def __repr__(self):
    return "Database Object"

	
  def __createFile__(self):
    """
    Creates a new File. (Do not call this as a script).
    """
    if not self.directory == "./":
      if not path.exists(f"./{self.directory}"):
        os.mkdir(self.directory)
      
    if not os.path.isfile(f'{self.path}'):
      with open(f'{self.path}', 'w') as db:
        pass
    else: 
      pass
	
  def all(self):
    """
    Returns all the information in the database.
    """

    if not path.exists(f'{self.path}'):
      self.__createFile__()
    rDB = open(f'{self.path}', 'r')
    read = rDB.read()
    if read == '':
      rDB.close()
      wDB = open(f'{self.path}', 'w')
      finalData = json.dumps({f"{self.name}": []})
      wDB.write(finalData)
      wDB.close()
      rDB = open(f'{self.path}', 'r')
      read = rDB.read()
      rDB.close()
      return json.loads(read)
    else:
      rDB.close()
      return json.loads(read)
	
  def get(self, key):
    """
    Returns the value of the entered key.
    """
    
    currentDB = self.all()
    arr = currentDB[f'{self.name}']
    for x in range(len(arr)):
      if arr[x]['key'] == key:
        return arr[x]['data']
    return print(colored(f'Error: \"{key}\" not found in database.', 'red'))
	
  def set(self, key, data):
    """
    Overwrites current data assigned to specified key, if none found creates new object to assign data to under entered key.
    """
    currentDB = self.all()
    initData = {'key': key, 'data': data}
    arr = currentDB[f'{self.name}']
    wDB = open(f'{self.path}', 'w')
    for x in range(len(arr)):
      if arr[x]['key'] == key:
        arr[x] = {"key": key, "data": data}
        finalData = json.dumps({f"{self.name}": arr})
        wDB.write(finalData)
        wDB.close()
        return data
    arr.append(initData)
    finalData = json.dumps({f"{self.name}": arr})
    wDB.write(finalData)
    wDB.close()
    return data
	
  def delete(self, key):
    """"
    Deletes the specified key from the database.
    """

    if key == 'all':
      wDB = open(f'{self.path}', 'w')
      finalData = json.dumps({f"{self.name}": []})
      wDB.write(finalData)
    else:
      currentDB = self.all()
      arr = currentDB[f'{self.name}']
      wDB = open(f'{self.path}', 'w')
      for x in range(len(arr)):
        if arr[x]['key'] == key:
          del arr[x]
          finalData = json.dumps({f"{self.name}": arr})
          wDB.write(finalData)
          wDB.close()
          return
      finalData = json.dumps({f"{self.name}": arr})
      wDB.write(finalData)
      wDB.close()
      return print(colored(f'Error: \"{key}\" not found in database.', 'red'))
      
	

  def subtract(self, key, data):
    """
    Subtracts from the value of specified key in database.
    """
    currentDB = self.all()
    arr = currentDB[self.name]
    for x in range(len(arr)):
      if arr[x]['key'] == key:
        if type(data) is int or type(data) is float:
          if type(arr[x]['data']) is int or type(arr[x]['data']) is float:
            arr[x]['data'] -= data
            finalData = json.dumps({f"{self.name}": arr})
            wDB = open(f'{self.path}', 'w')
            wDB.write(finalData)
            wDB.close()
            return arr[x]['data']
          else:
            varType = type(arr[x]['data'])
            return print(colored(f'Error: cannot add a int or float to a {varType}.', 'red'))
        else:
          varType = type(data)
          return print(colored(f'Error: expected type - \'int\' or \'float\', got {varType}.', 'red'))
	
  
  def unlink(self):
    """
    Unlinks a database, and deletes all associated data
    """

    if path.exists(f'DB/{self.name}.json'):
      os.remove(f'DB/{self.name}.json')

  def exists(self, key):
    """
    Checks if a key exists in the database.
    """
    currentDB = self.all()
    arr = currentDB[self.name]

    for x in range(len(arr)):
      if arr[x]['key'] == key:
        return True;
    
    return False;

  def add(self, key, data):
    """
    Adds a specified value to a key in the database
    """
		
    currentDB = self.all()
    arr = currentDB[self.name]
    for x in range(len(arr)):
      if arr[x]['key'] == key:
        if type(data) is int or type(data) is float:
          if type(arr[x]['data']) is int or type(arr[x]['data']) is float:
            arr[x]['data'] += data;
            finalData = json.dumps({f"{self.name}": arr})
            wDB = open(f'{self.path}', 'w')
            wDB.write(finalData)
            wDB.close()
            return arr[x]['data'];
          else:
            varType = type(arr[x]['data'])
            return print(colored(f'Error: cannot add a int or float to a {varType}.', 'red'))
        else:
          varType = type(data)
          return print(colored(f'Error: expected type - \'int\' or \'float\', got {varType}.', 'red'))
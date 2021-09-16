import platform, json, yaml, os
from pathlib import Path
from yaml import Loader, Dumper

class Files:
    def __init__(self):
        pass

    class Path:
        def __init__(self):
            pass

        def format(self, 
            path: str
        ) -> str:
            ''' Returns an OS friendly path string.
            
            -----
            * `path` (str) : A path to a directory or file.
            * `return` (str) : Properly formatted path string.
            '''
            path = path.replace('"','')
            path = path.replace("'",'')
            if platform.system() == 'Windows':
                return path.replace('/','\\')
            else:
                return path.replace('\\','/')

        def user_specified(self, file_type):
            file_path = Files().Path().format(input("Please provide path to " + file_type + ":"))
            is_file_opened = False
            while is_file_opened is False:
                try:
                    file = open(file_path)
                    is_file_opened = True
                except:
                    print("Please enter a valid file path.")
                    file_path = Files().Path().format(input("Please provide path to " + file_type + ":"))
            return file_path

        def is_mk_dir(self, path):
            path = Path(path)
            if not os.path.isdir(path):
                os.mkdir(path)
            return path

        def cwd(self, file):
            return Path(os.path.dirname(os.path.realpath(file)))

    class Json:
        def __init__(self):
            pass
        def write(self, 
            data, 
            path : str
        ):
            '''Dumps incoming python data into a JSON file at `path`.
            
            -----
            * `data` (dict,list,tuple) : Any JSON dump friendly python data structure.
            * `path` (str) : Path to JSON output file.
            '''
            with open(path, "w") as output_file:
                json.dump(data, output_file)

        def read(self, 
            path : str
        ):
            '''Loads JSON data from a file at the provided path.
            
            -----
            * `path` (str) : Path to JSON file.
            * `return` (dict,list,tuple) : Returns a python data structure.
            '''
            with open(path,'r') as input_file:
                return json.load(input_file)

    class Yaml:
        def __init__(self):
            pass
        def write(self, 
            data, 
            path : str
        ):
            '''Dumps incoming python data into a YAML file at `path`.
            
            -----
            * `data` (dict,list,tuple) : Any YAML dump friendly python data structure.
            * `path` (str) : Path to YAML output file.
            '''
            with open(path, "w") as output_file:
                yaml.dump(data, output_file, Dumper=yaml.Dumper)

        def read(self, 
            path : str
        ):
            '''Loads YAML data from a file at the provided path.
            
            -----
            * `path` (str) : Path to YAML file.
            * `return` (dict,list,tuple) : Returns a python data structure.
            '''
            with open(path,'r') as input_file:
                return yaml.load(input_file, Loader=yaml.Loader)


    class Open:
        def __init__(self):
            pass

        def user_specified(self, file_type):
            file_path = Files().Path().format(input("Please provide path to " + file_type + ":"))
            is_file_opened = False
            while is_file_opened is False:
                try:
                    file = open(file_path)
                    is_file_opened = True
                except:
                    print("Please enter a valid file path.")
                    file_path = Files().Path().format(input("Please provide path to " + file_type + ":"))
            return open(file_path)
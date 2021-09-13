import yaml


def yaml_reader(path):
    
    try:
        a_yaml_file = open(f"{path}/buildpan.yaml")
        parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

        # tool version 
        yaml_reader.version = parsed_yaml_file["version"]

        # reading Project id 
        yaml_reader.project_id = parsed_yaml_file['projotectDetail']["projectid"]

        # Redeaing Platform and and its version 
        platform = parsed_yaml_file['projotectDetail']["platform"]
        temp_index=platform.find(":")
        yaml_reader.platform_ver = platform[temp_index + 1:].strip()
        yaml_reader.platform_name = platform[:temp_index].strip()

        # jobs
        jobs = parsed_yaml_file["jobs"]
    
    except:

        print("Invalid format")

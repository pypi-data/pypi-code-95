from buildpan import yaml_reader, platform_installer


def installer():
    try:
        
        platform_name = yaml_reader.yaml_reader.platform_name
        node_ver = yaml_reader.yaml_reader.platform_ver

        if platform_name == "node":
            platform_installer.node_installer(node_ver)
        elif platform_name == "":
            print("Please provide platform name")
        else:
            print("This name is not supported")
    
    except Exception as e:
        print(e)